from pathlib import Path
src=Path('render.py').read_text()
exec(src.split('proc=subprocess.Popen',1)[0])
W,H=1080,696; n=240
outfile='Vortex Threads - Matched Comparison.mp4'
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-threads','3','-movflags','+faststart',outfile],stdin=subprocess.PIPE)
pal=np.array([[60,172,146],[164,78,52],[192,158,91]],dtype=float)
def panel(d,shape_value,s,cx,eeye):
    # Identical camera function and particle/curve samples across panels.
    X,Y,D=camera(shape(P,shape_value),s)
    X=cx+.78*(X-360); Y=370+.78*(Y-419)
    dseg=(D[:,:-1]+D[:,1:])/2
    dep=np.clip((dseg+1.37)/2.74,0,1)
    clr=np.clip(eeye*(.16+.81*dep[...,None])+dep[...,None]*34,0,255).astype(np.uint8).reshape(-1,3).tolist()
    order=np.argsort(dseg.ravel()).tolist()
    x0=X[:,:-1].ravel().tolist();y0=Y[:,:-1].ravel().tolist()
    x1=X[:,1:].ravel().tolist();y1=Y[:,1:].ravel().tolist()
    widths=(1+(dep>.63)).ravel().tolist()
    for j in order:
        if j<59*(X.shape[1]-1) or j%(X.shape[1]-1)%3!=1:
            d.line((x0[j],y0[j],x1[j],y1[j]),fill=tuple(clr[j]),width=widths[j])
    x,y,z=camera(shape(seeds,shape_value),s)
    x=cx+.78*(x-360);y=370+.78*(y-419)
    for j in np.argsort(z):
        if z[j]<-.16: continue
        k=min(1,max(0,(z[j]+.16)/1.4)); r=.9+1.2*k
        d.ellipse((x[j]-r,y[j]-r,x[j]+r,y[j]+r),fill=(int(92+145*k),int(61+146*k),int(34+93*k)))
dt=tf/(n-1)
assert np.allclose(shape(P,0),shape(P,0.10))
assert np.allclose(shape(np.array([[0,np.pi/2]]),0)[0],0,atol=1e-12)
assert np.min(np.hypot(*shape(np.column_stack([np.zeros_like(u),u]),1)[:2]))>.53
yy,xx=np.ogrid[:H,:W]; illum=np.exp(-((yy-370)/390)**2-(((xx%540)-270)/530)**2)
bg=np.stack([6+4*illum,10+8*illum,13+9*illum],axis=-1)
bg=Image.fromarray(bg.astype(np.uint8))
ft=font(40,True); fs=font(25); fp=font(30,True); ffoot=font(21); fphase=font(17,True)
for i in range(n):
    s=i/(n-1);t=i*dt; im=bg.copy();d=ImageDraw.Draw(im)
    d.text((40,25),'VORTEX THREADS  /  CONTROL STUDY',font=ft,fill='#e8eedf')
    d.text((40,82),'Same Taylor–Green flow, starting threads, camera and time',font=fs,fill='#a8c5ba')
    d.line((40,124,1040,124),fill='#314442',width=1)
    d.text((40,143),'FIXED SPHERE',font=fp,fill='#8cc5b2')
    d.text((566,143),'SCRIPTED PINCH',font=fp,fill='#dfb382')
    stage='START: SPHERE' if s<.13 else ('COMPRESS' if s<.42 else ('OPEN HOLE' if s<.81 else 'TORUS'))
    d.text((566,188),stage,font=fphase,fill='#bda690')
    d.line((540,140,540,595),fill='#314442',width=1)
    sign=np.cos(P[:,:-1,0])*np.cos(P[:,:-1,1]); eeye=pal[np.where(sign>.10,0,np.where(sign<-.10,1,2))]
    panel(d,0,s,270,eeye); panel(d,s,s,810,eeye)
    if i==0:
        assert im.crop((20,217,520,545)).tobytes()==im.crop((560,217,1060,545)).tobytes()
    d.line((40,611,1040,611),fill='#314442',width=1)
    d.text((40,629),'Only the surface changes. The fluid motion does not create the hole.',font=ffoot,fill='#b8c5bf')
    d.rectangle((40,670,1040,674),fill='#314442'); d.rectangle((40,670,40+1000*s,674),fill='#77b7a8')
    if i in (0,115,239): im.save(f'compare-{i}.png')
    p.stdin.write(im.tobytes())
    P=step(P,t,dt);seeds=step(seeds,t,dt)
p.stdin.close()
assert p.wait()==0
