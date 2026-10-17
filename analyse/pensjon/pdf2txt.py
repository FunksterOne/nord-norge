import pypdf,sys
for f in sys.argv[1:]:
    r=pypdf.PdfReader(f); t='\n'.join(('\n--- side %d ---\n'%(i+1))+(p.extract_text() or '') for i,p in enumerate(r.pages))
    open(f.rsplit('.',1)[0]+'.txt','w',encoding='utf-8').write(t); print(f,len(r.pages),len(t))
