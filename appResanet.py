#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet


app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte ,)

	aujourdhui = datesResanet.getDateAujourdhuiISO()
	
	aujourdhuis = datesResanet.convertirDateISOversFR(aujourdhui)

	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	jours  = [ "Lundi" , "Mardi" , "Mercredi" , "Jeudi" , "Vendredi" ]
	
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )
		
		if uneDateISO <= aujourdhui :
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False

		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False
			
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
			
			
		dates.append( uneDate )
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False
		
	
	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant , aujourdhuis = aujourdhuis , jours = jours )

	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )


@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	
	return render_template( 'vueConnexionGestionnaire.html' , echecConnexion = False , saisieIncomplete = False ,tentative = False )

@app.route( '/gestionnaire/seConnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	nomConnexion = request.form[ 'nomConnexion' ]
	mdp = request.form[ 'mdp' ]
	
	if nomConnexion != "" and mdp != "" :
		gestionnaire = modeleResanet.seConnecterGestionnaire( nomConnexion , mdp )
		if len(gestionnaire) != 0 :
			session[ 'login' ] = gestionnaire[ 'login' ]
			session[ 'nom' ] = gestionnaire[ 'nom' ]
			session[ 'prenom' ] = gestionnaire[ 'prenom' ]
			session[ 'mdp' ] = mdp
			
			return redirect( '/gestionnaire/listerPersonnelAvecCarte' )
			
		
		else :
			return render_template( 'vueConnexionGestionnaire.html' , echecConnexion = True , saisieIncomplete = False )			
	else :
		return render_template( 'vueConnexionGestionnaire.html' , saisieIncomplete = True  , echecConnexion = False  )
		
		
@app.route( '/gestionnaire/listerPersonnelAvecCarte' , methods = [ 'GET' ] )
def listerPersonnelsAvecCarte() :		
	aujourdhui = datesResanet.getDateAujourdhuiISO()	
	aujourdhuis = datesResanet.convertirDateISOversFR(aujourdhui)
	personnels = modeleResanet.getPersonnelsAvecCarte()
			
	return render_template( 'vuePersonnelAvecCarte.html' , aujourdhuis = aujourdhuis , personnels = personnels )

@app.route( '/gestionnaire/listerPersonnelSansCarte' , methods = [ 'GET' ] )
def listerPersonnelsSansCarte() :		
	aujourdhui = datesResanet.getDateAujourdhuiISO()	
	aujourdhuis = datesResanet.convertirDateISOversFR(aujourdhui)
	personnels = modeleResanet.getPersonnelsSansCarte()
			
	return render_template( 'vuePersonnelSansCarte.html' , aujourdhuis = aujourdhuis , personnels = personnels )
	
@app.route( '/gestionnaire/listerPersonneAvecCarte/bloquer' , methods=['POST'] )
def desactiverCarte() :
	numeroCarte = request.form[ 'matricule' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.bloquerCarte(numeroCarte)
	return redirect( '/gestionnaire/listerPersonnelAvecCarte' )
	
@app.route( '/gestionnaire/listerPersonneAvecCarte/activer' , methods=['POST'] )
def activeeCarte() :
	numeroCarte = request.form[ 'matricule' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.activerCarte(numeroCarte)
	return redirect( '/gestionnaire/listerPersonnelAvecCarte' )

@app.route( '/gestionnaire/listerPersonneAvecCarte/initMdp' , methods=['POST'] )
def initMDP() :
	numeroCarte = request.form[ 'matricule' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.reinitialiserMdp(numeroCarte)
	return redirect( '/gestionnaire/listerPersonnelAvecCarte' )
		
@app.route( '/gestionnaire/seDeconnecter' )
def seDeconnecterGestionnaire() :
	session.pop( 'login' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	session.pop( 'mdp' , None )
	return redirect( '/' )
		
if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )
