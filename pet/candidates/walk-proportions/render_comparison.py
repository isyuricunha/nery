"""Package actual GIF playback for proportion review, without changing runtime."""
from pathlib import Path
import base64

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nery · Proporções da caminhada</title><style>body{background:#181210;color:#eee;font:15px system-ui;line-height:1.5;margin:0}main{max-width:1000px;padding:30px 20px;margin:auto}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}figure{background:#211915;padding:18px 10px;margin:0;border:1px solid #574035;border-radius:10px}img{display:block;width:192px;height:208px;max-width:100%;object-fit:contain;margin:auto}figcaption{margin-bottom:14px;text-align:center}p{color:#b9a195}@media(max-width:600px){.grid{grid-template-columns:1fr}}</style><main><h1>Nery · Proporções da caminhada</h1><p>GIFs na velocidade normal. A e B são candidatas de proporção; a passada ainda será finalizada com o corpo escolhido.</p><div class="grid">'''
    for title,path in [('Anterior',ROOT/'pet/preview/walk-16.gif'),('A · mais arredondada',HERE/'rounded.gif'),('B · articulada com pernas mais cheias',HERE/'articulated.gif')]:
        url='data:image/gif;base64,'+base64.b64encode(path.read_bytes()).decode()
        html+=f'<figure><figcaption>{title}</figcaption><img src="{url}" alt="{title}" width="192" height="208"></figure>'
    html+='</div><p>A candidata magrinha foi retirada. A correção de Failed permanece salva no marco <code>2c0aeff</code>, independente destas prévias.</p></main></html>'
    (HERE/'comparison.html').write_text(html,encoding='utf-8')

if __name__=='__main__':
    main()
