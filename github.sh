#!/bin/bash
# Initialiser le depot github et deposer des fichiers

git remote add origin https://github.com/Sedastien/resanet
git init

while [ nomFichier != 'test.txt' ]
do
	nomFichier="/home/developpeur/Bureau/projets/*"
	git add $nomFichier
	git status
	git commit -a -m 'resanet'
	git push -u origin master
done

