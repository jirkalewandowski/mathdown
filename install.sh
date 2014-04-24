#!/bin/bash
DATADIR=~/.mdma
EXECDIR=./

mkdir -p ${DATADIR}
cp markmath.py ${DATADIR}
cp template.tex ${DATADIR}

bash << EOF
echo "MDPATH=$DATADIR" > ${EXECDIR}/mathdown
echo '\${MDPATH}/markmath.py \$1.mdma > \$1.mdtmp' >> ${EXECDIR}/mathdown
echo 'pandoc -f markdown --template=\${MDPATH}/template.tex -s -o \$1.tex \$1.mdtmp' >> ${EXECDIR}/mathdown
echo 'pandoc -f markdown --template=\${MDPATH}/template.tex -s -o \$1.pdf \$1.mdtmp' >> ${EXECDIR}/mathdown
echo 'rm \$1.mdtmp' >> ${EXECDIR}/mathdown
chmod +x ${EXECDIR}/mathdown
EOF
sudo mv mathdown /usr/bin/