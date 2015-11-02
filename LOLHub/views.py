from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from collections import OrderedDict
from riotwatcher.riotwatcher import RiotWatcher, LoLException, error_404
from LOLHub.models import *
from django import template
from django.http import HttpResponse
import json
from django.core.serializers.json import  DjangoJSONEncoder
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import time
import requests

# Constantes
w = RiotWatcher(key = settings.RIOT_API_KEY, default_region='lan')

# Create your views here.
def Index(request):
	return render_to_response('Index.html', context_instance = RequestContext(request))


def StatsCard(request,sname=None):	

	if sname != None:
		me = w.get_summoner(name = sname)
		lEntry = None
		try:
			lEntry = w.get_league_entry(summoner_ids=(me['id'],))
			if(lEntry[str(me['id'])][0]['queue'] != 'RANKED_SOLO_5x5'):
				# Debe tener ranking en solo Q para poder salir aqui wei
				return render_to_response('Card.html', {'showSC': False, 'showError': True}, context_instance = RequestContext(request))		
		except LoLException as e:
			if e.error == error_404:
				return render_to_response('Card.html', {'showSC': False, 'showError': True}, context_instance = RequestContext(request))		
			else:
				raise e

		tier = lEntry[str(me['id'])][0]['tier']
		wins = lEntry[str(me['id'])][0]['entries'][0]['wins']
		losses = lEntry[str(me['id'])][0]['entries'][0]['losses']
		WLR = round((wins / float((wins+losses)) ) * 100,2)
		lp = lEntry[str(me['id'])][0]['entries'][0]['leaguePoints']
		division = lEntry[str(me['id'])][0]['entries'][0]['division']
		rankedstats = w.get_ranked_stats(summoner_id=me['id'])
		#champ0Id = rankedstats['champions'][0]['id']
		#champInfo = w.static_get_champion(champ_id=champ0Id,region='lan', champ_data=('image',))
		xd = Resumir(rankedstats['champions'])
		
		
		# static_get_champion(self, champ_id, region=None, locale=None, version=None, champ_data=None):
		
		#print xd
		kda = round((xd['r']['stats']['totalAssists'] + xd['r']['stats']['totalChampionKills']) / float(xd['r']['stats']['totalDeathsPerSession']) ,2)
		td = xd['r']['stats']['totalDoubleKills'] 
		tt = xd['r']['stats']['totalTripleKills']
		tq = xd['r']['stats']['totalQuadraKills'] 
		tp = xd['r']['stats']['totalPentaKills']
		

		gInfo ={'w':wins,'l':losses,'wlRatio':WLR, 'kda':kda}
		mks = {'d':td,'t':tt,'q':tq,'p':tp}
		champs = w.static_get_champion_list(region='na', data_by_id=True)

		champName = champs['data'][str(xd['p']['id'])]['key']

		xd['s']['info'] = champs['data'][str(xd['s']['id'])]
		xd['s']['kda'] = round((xd['s']['stats']['totalAssists'] + xd['s']['stats']['totalChampionKills']) / float(xd['s']['stats']['totalDeathsPerSession']),2) 

		xd['t']['info'] = champs['data'][str(xd['t']['id'])]
		xd['t']['kda'] = round((xd['t']['stats']['totalAssists'] + xd['t']['stats']['totalChampionKills']) / float(xd['t']['stats']['totalDeathsPerSession']),2)

		xd['c']['info'] = champs['data'][str(xd['c']['id'])]
		xd['c']['kda'] = round((xd['c']['stats']['totalAssists'] + xd['c']['stats']['totalChampionKills']) / float(xd['c']['stats']['totalDeathsPerSession']),2)

		return render_to_response('Card.html', {'showSC': True,'gInfo': gInfo, 'mks':mks,'SubMejores':xd, 'champ':champName, 'SummonerName':me['name'],'profileId':me['profileIconId'], 'Id':me['id'],'Tier':tier,'Division':division}, context_instance = RequestContext(request))
	return render_to_response('Card.html', {'showSC': False}, context_instance = RequestContext(request))				

def Resumir(o):
	size = len(o)
	primero = 0
	segundo = 0
	tercero = 0
	cuarto = 0
	s = 0
	resumen = 0
	# if size > 1:
	# 	primero = o[1]
	# 	s = 2
	# 	if size > 2 and o[2]['id'] != 0:
	# 		if()
	# 		segundo = o[2]
	# 		s = 3
	# 		if size > 3:
	# 			if(o[3]['id'] != 0)
	# 				tercero = o[3]
	# 			s = 4
	
	for x in range(s, size-1):
		if o[x]['id'] != 0:
			tag = None
			
			if primero == 0 or o[x]['stats']['totalSessionsPlayed'] > primero['stats']['totalSessionsPlayed']:
				primero,o[x] = o[x],primero

			if size > 1 and (segundo == 0 or o[x]['stats']['totalSessionsPlayed'] > segundo['stats']['totalSessionsPlayed']):
				segundo,o[x] = o[x],segundo

			if size > 2 and (tercero == 0 or o[x]['stats']['totalSessionsPlayed'] > tercero['stats']['totalSessionsPlayed']):
				tercero,o[x] = o[x],tercero

			if size > 3 and (cuarto == 0 or o[x]['stats']['totalSessionsPlayed'] > cuarto['stats']['totalSessionsPlayed']):
				cuarto,o[x] = o[x],cuarto
		else:
			resumen = o[x]

	return {'p':primero,'s':segundo,'t':tercero, 'c': cuarto, 'r': resumen}


def AddToHubP(request):
	summoner = None
	try:
		summoner = w.get_summoner(name=request.POST['sname'])
	except Exception as e:
		return render_to_response('AddToHub.html', {'Error': True}, context_instance = RequestContext(request))
		

	runas = w.get_rune_pages(summoner_ids=(summoner['id'],), region='lan')
	error_runas = True
	for x in runas[str(summoner['id'])]['pages']:
		if x['name'] == 'LOLHub': #Runepage name Identificator
			error_runas = False

	if error_runas:
		return render_to_response('AddToHub.html', {'Error': True}, context_instance = RequestContext(request))
		# raise LoLException("Debes renombrar una pagina de runas con el nombre LOUHub.","Debes renombrar una pagina de runas con el nombre LOUHub.")


	ii = Summoners()
	ii.Nombre = summoner['name']
	ii.SummonerIcon = summoner['profileIconId']
	ii.Id = summoner['id']


	try:
		rankedEntry = w.get_league_entry(summoner_ids=(summoner['id'],))
		if(rankedEntry[str(summoner['id'])][0]['queue'] == 'RANKED_SOLO_5x5'):
			ii.Tier = rankedEntry[str(summoner['id'])][0]['tier']
			ii.Division = rankedEntry[str(summoner['id'])][0]['entries'][0]['division']
			ii.LP = rankedEntry[str(summoner['id'])][0]['entries'][0]['leaguePoints']
			ii.Score = getLeagueScore(ii.Tier,ii.Division,ii.LP)
		else:
			raise LoLException(error_404,'Es unranked el pibe.')
	except LoLException as e:
		if e.error == error_404:
			ii.Tier = 'provisional'.upper()
			ii.Division = '0'
			ii.LP = '0'
			ii.Score = summoner['summonerLevel']
	
	ii.Lv = summoner['summonerLevel']
	ii.save()
	
	return SocialHub(request)

def AddToHub(request):
	return render_to_response('AddToHub.html', {'Error': False}, context_instance = RequestContext(request))

def SocialHub(request):
	#Order by score
	summoners = Summoners.objects.order_by('-Score')


	TiersClasses = OrderedDict({ 
		'PROVISIONAL': 'default',
		'BRONZE': 'bronze', 
		'SILVER': 'silver',
		'GOLD':'warning', 
		'PLATINUM':'success',
		'DIAMOND':'info',
		'MASTERS': 'default',
		'CHALLENGER': 'default'
	})
	
	# plays = requests.get('https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channelId}&order=date&key={googlekey}'
	# 					 .format(
	# 					 	googlekey= settings.GOOGLE_API_KEY, 
	# 					 	channelId = 'UC_Axbyee5-frfiW5xkZl3ew'
	# 					 	)
	# 					 ).json()

	plays = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlistId}&key={googlekey}'
						 .format(
						 	googlekey= settings.GOOGLE_API_KEY, 
						 	playlistId = 'PLpK9SZ4LA7R2YDzZftvRspn4TMPj6irbV'
						 	)
						 ).json()

	streamers = Streamers.objects.all()

	return render_to_response('SocialHub.html',{'plays':plays['items'], 'tc': TiersClasses,'streamers':streamers, 'summoners': summoners}, context_instance = RequestContext(request))

def getLeagueScore(Tier,Division,LP):
	Tiers = { 
		'BRONZE': '1', 
		'SILVER': '2',
		'GOLD': '3', 
		'PLATINUM': '4',
		'DIAMOND': '5',
		'MASTERS': '6',
		'CHALLENGER': '7'
	}

	Divisiones = {'I':'5','II':'4','III':'3','IV':'2', 'V':'1'}

	alp = str(LP)
	if len(alp) == 1:
		alp+='00'
	if len(alp) == 2:
		alp+='0'
	return	int(Tiers[Tier]+Divisiones[Division]+alp)


@staff_member_required
def AddToStreamersP(request):
	s = Streamers()
	s.Nombre = request.POST['name']
	s.save()

	return SocialHub(request)

@staff_member_required
def AddToStreamers(request):
	return render_to_response('AddToStreamers.html', context_instance = RequestContext(request))

@csrf_exempt
def matchActual(request):
	payload = json.loads(request.body.decode('utf-8'))
	idx = payload['id']
	try:
		m = w.get_current_game(summoner_id = idx, platform_id = 'LA1', region='lan')
		return HttpResponse(json.dumps({ 'Match': m }))
	except: 
		return HttpResponse(json.dumps({ 'Match': None }))

@csrf_exempt
def GetChamps(request):	
	return HttpResponse(json.dumps(w.static_get_champion_list(region='na', data_by_id=True)))

@csrf_exempt
def GetSpells(request):
	return HttpResponse(json.dumps(w.static_get_summoner_spell_list(region='na', data_by_id=True)))

@staff_member_required
@csrf_exempt
def UpdateSummoners(request):
	summoners = Summoners.objects.all()

	for x in summoners:
		summoner = w.get_summoner(name = x.Nombre)
		x.SummonerIcon = summoner['profileIconId']
		x.Id = summoner['id']

		try:
			rankedEntry = w.get_league_entry(summoner_ids=(x.Id,))
			if(rankedEntry[str(x.Id)][0]['queue'] == 'RANKED_SOLO_5x5'):
				x.Tier = rankedEntry[str(x.Id)][0]['tier']
				x.Division = rankedEntry[str(x.Id)][0]['entries'][0]['division']
				x.LP = rankedEntry[str(x.Id)][0]['entries'][0]['leaguePoints']
				x.Score = getLeagueScore(x.Tier,x.Division,x.LP)
			else:
				raise LoLException(error_404,'Es unranked el pibe.')
		except LoLException as e:
			if e.error == error_404:
				x.Tier = 'provisional'.upper()
				x.Division = '0'
				x.LP = '0'
				x.Score = summoner['summonerLevel']
		
		x.Lv = summoner['summonerLevel']
		x.save()
		time.sleep(5)

	return HttpResponse(json.dumps({'rs':'Actualizado satisfactoriamente.'}))

