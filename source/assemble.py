import json, os
H=os.path.dirname(os.path.abspath(__file__))
c=json.load(open(H+'/out/content.json'))
def js(o): return json.dumps(o,ensure_ascii=False).replace('</','<\\/').replace(' ','\\u2028')
app=open(H+'/app.html').read()
app=app.replace('/*__CONTENT__*/null',js(c)).replace('/*__RUNNER__*/null',js(open(H+'/runner.py').read()))
open(H+'/out/lime.html','w').write(app)
print(len(app))
