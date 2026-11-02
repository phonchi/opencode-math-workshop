"""獨立實算改版教材用到的數字。python 由 starter 環境執行。"""
import numpy as np, warnings
from sklearn.datasets import load_digits
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score, confusion_matrix
from scipy.optimize import linear_sum_assignment
warnings.filterwarnings('ignore')
d=load_digits(); X,y=d.data,d.target; n=len(X)
print('## opener zero pixels', np.flatnonzero(X.std(0)==0))
print('## Lab1 silhouette best k (k=2..12, random_state=0, n_init=10)')
def best(Z,name):
    s={k:silhouette_score(Z,KMeans(k,n_init=10,random_state=0).fit_predict(Z)) for k in range(2,13)}
    b=max(s,key=s.get); print(f'{name}: best k={b} sil={s[b]:.4f}; k=10 sil={s[10]:.4f}')
best(X,'raw'); best(StandardScaler().fit_transform(X),'std'); best(PCA(2,random_state=0).fit_transform(X),'pca2')
l=KMeans(10,n_init=10,random_state=0).fit_predict(X)
cm=confusion_matrix(y,l); r,c=linear_sum_assignment(-cm)
print('## k=10 raw: direct acc %.3f matched acc %.3f ARI %.3f'%((l==y).mean(),cm[r,c].sum()/n,adjusted_rand_score(y,l)))
perm=(l+1)%10; print('relabel: direct acc %.3f ARI %.3f'%((perm==y).mean(),adjusted_rand_score(y,perm)))
print('## Lab2 check x bug')
K=10; sk=PCA(K,svd_solver='full',random_state=0).fit(X); mu=X.mean(0); Xc=X-mu
def pca(bug=None):
    A=X if bug=='nocenter' else Xc
    den=n if bug=='denom_n' else n-1
    C=A.T@A/den; ev,V=np.linalg.eigh(C); i=np.argsort(ev)[::-1]; ev,V=ev[i],V[:,i]
    W=V[:K].copy() if bug=='rows' else V[:,:K].T
    tot=ev[:K].sum() if bug=='ratio_topk' else ev.sum()
    return ev[:K],W,ev[:K]/tot
skrec=sk.inverse_transform(sk.transform(X)); skm=((X-skrec)**2).mean()
print('bug | ratio-sk | ratio-sum | min|cos| | recMSE diff | orth | eigval diff')
for b in [None,'ratio_topk','denom_n','nocenter','rows']:
    ev,W,r=pca(b); cos=np.abs((W*sk.components_).sum(1))
    W_o=W; rec=(Xc@W_o.T)@W_o+mu; m=((X-rec)**2).mean()
    print(f"{str(b):11s} {np.abs(r-sk.explained_variance_ratio_).max():.3e} sum={r.sum():.6f} {cos.min():.6f} {abs(m-skm):.3e} {np.abs(W@W.T-np.eye(K)).max():.3e} {np.abs(ev-sk.explained_variance_).max():.4f}")
print('sk sum ratio %.4f first %.4f'%(sk.explained_variance_ratio_.sum(),sk.explained_variance_ratio_[0]))
print('## Lab3')
m=(y==3)|(y==8); A=X[m]/16; t=(y[m]==8).astype(float); Xb=np.c_[A,np.ones(len(A))]; print('shape',Xb.shape,'constant cols',int((A.std(0)==0).sum()),np.flatnonzero(A.std(0)==0).tolist())
sg=lambda z:1/(1+np.exp(-z))
loss=lambda w:np.mean(np.logaddexp(0,Xb@w)-t*(Xb@w)); grad=lambda w:Xb.T@(sg(Xb@w)-t)/len(t)
msel=lambda w:np.mean((sg(Xb@w)-t)**2); 
def mseg(w):
    z=Xb@w;p=sg(z);return Xb.T@(2*(p-t)*p*(1-p))/len(t)
w0=np.random.RandomState(0).normal(size=65)*0.01
def gc(L,G,h=1e-5):
    g=G(w0); fd=np.array([(L(w0+h*e)-L(w0-h*e))/(2*h) for e in np.eye(65)]);return np.abs(g-fd).max(),g,fd
print('correct abs err %.2e'%gc(loss,grad)[0]); a,g,fd=gc(loss,grad)
zero=np.flatnonzero(g==0); print('exact zero grad dims',zero.tolist())
with np.errstate(all='ignore'): rel=np.abs(g-fd)/np.abs(g)
print('naive rel err max (nan?)',np.nanmax(rel),'has nan',np.isnan(rel).any(),'inf',np.isinf(rel).any())
print('mse+mse abs err %.2e'%gc(msel,mseg)[0]); print('grad*2 abs err %.3f'%gc(loss,lambda w:2*grad(w))[0])
print('sign flip loss check y=1,z=0: L=log(1+1)-0=%.4f; y=1,z=large(10): %.6f; y=1,z=-10: %.4f'%(np.log(2),np.logaddexp(0,10)-10,np.logaddexp(0,-10)+10))
