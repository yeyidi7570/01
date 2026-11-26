"""Draw verification SVGs from a single structured JSON input.

Usage: python redraw.py <content.json> <new-output-directory>
"""
import argparse
from html import escape
import json
from pathlib import Path

BLUE = '#253e67'
INK = '#152637'
RED = '#ab392f'

def label(x, y, text, anchor='middle', color=INK, size=15):
    return (f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" '
            f'fill="{escape(color)}" font-size="{size}">{escape(str(text))}</text>')

def segment(x1, y1, x2, y2, color=INK, width=2, arrow=False, dash=None):
    marker = ' marker-end="url(#tip)"' if arrow else ''
    dash_style = f' stroke-dasharray="{escape(dash)}"' if dash else ''
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{escape(color)}" stroke-width="{width}"{marker}{dash_style}/>')

def svg(width, height, markup, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img"><title>{escape(title)}</title>'
            '<defs><marker id="tip" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>'
            f'<rect width="{width}" height="{height}" fill="white"/>'
            f'<g font-family="sans-serif">{markup}</g></svg>\n')

def motion(data):
    coords = {pt['id']: 110 + 190*pt['slot'] for pt in data['points']}
    baseline = 104
    out = [segment(min(coords.values()), baseline, max(coords.values()), baseline, BLUE, 3)]
    bracketed = {d['start']: 'end' for d in data.get('distances',[]) if d.get('annotation') == 'brace_below_segment'}
    bracketed.update({d['end']: 'start' for d in data.get('distances',[]) if d.get('annotation') == 'brace_below_segment'})
    for pt in data['points']:
        x = coords[pt['id']]
        out.append(f'<circle cx="{x}" cy="{baseline}" r="4.5" fill="{BLUE}"/>')
        if pt.get('label'):
            anchor = bracketed.get(pt['id'], 'middle')
            dx = {'end': -9, 'middle': 0, 'start': 9}[anchor]
            out.append(label(x + dx, 127, pt['label'], anchor))
    for move in data['arrows']:
        x = coords[move['from']]
        direction = {'right':1,'left':-1}[move['direction']]
        length = {None:52,'longer':67,'shorter':43}[move.get('length_hint')]
        tip = x+direction*length
        out.extend([segment(x,baseline,x,73,BLUE), segment(x,73,tip,73,BLUE,2,True)])
        out.append(label((x+tip)/2,61,move['label']))
    if data.get('flag_at'):
        x=coords[data['flag_at']]
        out.append(segment(x,baseline,x,42,BLUE))
        out.append(f'<path d="M{x} 42h25l-5 7 5 7h-25z" fill="{RED}"/>')
    for dist in data.get('distances',[]):
        a,b=coords[dist['start']],coords[dist['end']]
        if dist.get('annotation')=='brace_below_segment':
            out.append(f'<path d="M{a} 110Q{a} 136 {(a+b)/2} 138Q{b} 136 {b} 110" fill="none" stroke="{BLUE}"/>')
        out.append(label((a+b)/2,158,dist['label']))
    if data.get('unknown_label'):
        out.append(label(max(coords.values())+116,49,data['unknown_label']))
    for a in data.get('annotations',[]):
        if a['kind']!='forward_arrow_label':
            raise ValueError(f'Unsupported annotation: {a["kind"]}')
        x=coords[a['from']]
        end=x+216*{'right':1,'left':-1}[a['direction']]
        out.append(segment(x,baseline,end,baseline,a['color'],2,True))
        out.append(label((x+end)/2,baseline-12,a['label']))
    if data.get('formula'):
        formula=data['formula']
        if 'formula_tokens' in data:
            content=''.join(
                escape(t['text']) if 'subscript' not in t else
                f"{escape(t['text'])}<tspan baseline-shift='sub' font-size='11'>{escape(t['subscript'])}</tspan>"
                for t in data['formula_tokens'])
            out.append(f'<text x="300" y="146" text-anchor="middle" fill="{INK}" font-size="16">{content}</text>')
        else:
            out.append(label(300,146,formula))
    return 600,178,''.join(out)

def chart(data):
    x_ticks,y_ticks=data['x_ticks'],data['y_ticks']
    vertices=[v for series in data['series'] for v in series['vertices']]
    xe,ye=data.get('grid_extent',[max(x for x,y in vertices),max(y for x,y in vertices)])
    grid=data.get('grid_cells')
    y_scale = 28 * grid['x'] / grid['y'] if grid and grid.get('shape')=='square' else 1/3
    px,py=lambda x: 64+x*28,lambda y: 256-y*y_scale
    assert max(x for x,y in vertices)<=xe and max(y for x,y in vertices)<=ye
    out=[]
    if grid:
        for x in range(0,xe+1,grid['x']):
            out.append(segment(px(x),py(0),px(x),py(ye),'#d7e3ef',1))
        for y in range(0,ye+1,grid['y']):
            out.append(segment(px(0),py(y),px(xe),py(y),'#d7e3ef',1))
    out.extend([segment(px(0),py(0),px(xe)+11,py(0),arrow=True),
                segment(px(0),py(0),px(0),py(ye)-11,arrow=True),
                label(px(xe)+17,py(0)+3,data['x_label'],'start'),
                label(px(0)-9,py(ye)-16,data['y_label'],'end')])
    for x in x_ticks:
        out.append(segment(px(x),py(0),px(x),py(0)+5))
        out.append(label(px(x),py(0)+23,x))
    for y in y_ticks:
        if y:
            out.append(segment(px(0)-5,py(y),px(0),py(y)))
            out.append(label(px(0)-10,py(y)+5,y,'end'))
    for i,series in enumerate(data['series']):
        points=' '.join(f'{px(x):.2f},{py(y):.2f}' for x,y in series['vertices'])
        color=escape(series['color'])
        out.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3.2" stroke-linejoin="round"/>')
        lx=68+i*156
        out.extend([segment(lx,298,lx+20,298,series['color'],3),
                    label(lx+26,303,series['name'],'start')])
    if 'shared_path' in data:
        shared=data['shared_path']
        lookup={s['name']:s for s in data['series']}
        for a,b in zip(shared['vertices'],shared['vertices'][1:]):
            for name in shared['series']:
                v=lookup[name]['vertices']
                assert any(c==a and d==b for c,d in zip(v,v[1:]))
            name=shared['series'][0]
            out.append(segment(px(a[0]),py(a[1]),px(b[0]),py(b[1]),lookup[name]['color'],3,dash='7 6'))
        out.append(label(395,303,shared['label'],'start',size=13))
    return max(700,round(px(xe)+126)),322,''.join(out)

def walk(units):
    for obj in units:
        yield obj
        yield from walk(obj.get('elements',[]))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    data=json.loads(args.dataset.read_bytes())
    args.output.mkdir()
    count=0
    drawers={'motion_diagram':motion,'coordinate_graph':chart}
    for obj in walk(data['lesson']['units']):
        if obj['type']!='informative_image':
            continue
        relation,=obj['structured_description']['relations']
        width,height,content=drawers[relation['kind']](relation)
        slug='-'.join(obj['id'].split(':')[-2:])
        (args.output/f'{slug}.svg').write_text(svg(width,height,content,slug),encoding='utf-8')
        count+=1
    print(f'{count} SVG files')

if __name__=='__main__':
    main()
