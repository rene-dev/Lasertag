del *.gpi *.dri *.gpi *.gml *.gtp *.gbp
md platine
cd platine
del *.gtl *.gbl *.gts *.gbs *.gto *.gbo *.txt *.do
cd ..
move *.gtl platine
move *.gbl platine
move *.gts platine
move *.gbs platine
move *.gto platine
move *.gbo platine
move *.txt platine
move *.do platine
cd platine
del platine.zip

"C:\Program Files\7-Zip\7z" a -tzip platine.zip *.gtl *.gbl *.gts *.gbs *.gto *.gbo *.txt *.do

