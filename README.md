This was modified from [pip2pkgbuild](https://github.com/wenLiangcan/pip2pkgbuild/blob/master/pip2pkgbuild/pip2pkgbuild.py) entirely by **vibe coding**
(therefore no credit goes to me, go credit Grok), for the sole purpose of easing up the installation of some >10 CRUX ports around `python3-anndata`, 
needed by my `r4-anndata`. I do not use python for my work, but some of the tools I use need it. 

The other possibility was to do this, but CRUX exlicitly warns against it:
```
pip3 install anndata --break-system-package
```

So, here it is.
