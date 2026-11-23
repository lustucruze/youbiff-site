#!/usr/bin/env python3
"""Génère le site youbiff.fr (statique, GitHub Pages) dans le dossier OUT."""
import os, re, json, html, shutil, sys

SRC = os.environ.get('YB_SRC', '/home/claude/youbiff-site')          # dépôt existant (pages légales d'origine)
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/out'
B = os.path.dirname(os.path.abspath(__file__))
DOMAIN = 'https://youbiff.fr'
MAJ = '23 novembre 2026'
PRIX = '1,99 €'
ICONS = json.load(open(os.path.join(B, 'icons.json')))

# ---------- icônes ----------
CAR = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#A9441A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 16V11l2-5h10l2 5v5"></path><path d="M3 16h18v3H3z"></path><circle cx="7.5" cy="16" r="1.5"></circle><circle cx="16.5" cy="16" r="1.5"></circle></svg>'
APPLE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="#FFFFFF" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.6 2.1-3.7-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9-.8 0-2-.9-3.3-.9-1.7 0-3.3 1-4.2 2.5-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.2 2.6 1.3-.1 1.8-.8 3.3-.8s2 .8 3.3.8c1.4 0 2.2-1.2 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9-.1 0-2.8-1.1-2.8-4.2zM14 5.3c.7-.8 1.2-2 1-3.1-1 0-2.2.7-2.9 1.5-.6.7-1.2 1.9-1 3 1.1.1 2.2-.6 2.9-1.4z"/></svg>'
FLAME = ICONS['__flame'][1]

# ---------- données ----------
TOOLS = [  # slug, clé js, nom, description, catégorie, intro SEO
 ('budget-du-mois','budget','Budget du mois','Tes besoins, tes envies, ton épargne.','budget','Entre ce qui rentre (bourse, APL, job) et ce qui sort, combien il te reste vraiment ? Le calcul compare aussi ton budget au repère 50 / 30 / 20.'),
 ('payer-en-3-ou-4-fois','fractionne','Payer en 3 ou 4 fois','Le vrai coût, frais compris.','budget','Le paiement en plusieurs fois a souvent des frais. Calcule le coût total et le montant de chaque paiement avant de cliquer.'),
 ('mes-abonnements','abonnements','Mes abonnements','Ce qu’ils te coûtent sur 1 an et 5 ans.','budget','Musique, vidéo, forfait, sport : additionne tes abonnements et vois ce qu’ils te coûtent vraiment sur 1 an et sur 5 ans.'),
 ('cout-voiture','voiture','Le vrai coût d’une voiture','Assurance, essence, entretien : par mois.','budget','Assurance, carburant, entretien, parking : le coût réel d’une voiture par mois et par kilomètre, pas seulement le prix d’achat.'),
 ('premier-appart','appart','Mon premier appart','Tout ce qu’il faut payer avant d’avoir les clés.','appart','Dépôt de garantie, frais d’agence au maximum légal, premier loyer, assurance : la somme à prévoir pour entrer dans ton premier logement.'),
 ('coloc','coloc','Coloc : qui paie quoi','Loyer et factures partagés au juste prix.','appart','Parts égales ou selon la taille des chambres : calcule ce que chaque coloc paie pour le loyer et les factures.'),
 ('salaire-brut-net','salaire','Salaire brut → net','Job, stage, alternance : ce que tu touches.','job','Du brut au net : estime ce que tu touches vraiment pour un job étudiant, un stage ou une alternance.'),
 ('interets-composes','interets','Intérêts composés','Comment ton épargne grossit avec le temps.','epargne','Ce que tu as au départ, ce que tu ajoutes chaque mois, un taux : vois comment l’effet boule de neige fait grossir ton épargne.'),
 ('comparateur-livrets','livrets','Comparateur de livrets','Livret A, LDDS, LEP, Livret jeune.','epargne','Livret A, LDDS, LEP, Livret jeune : lequel te rapporte le plus selon ta somme, ta durée et ta situation, aux taux de 2026.'),
 ('micro-entreprise','micro','Micro-entreprise','Tes cotisations et ce qu’il te reste.','boite','Vente, service ou activité libérale : calcule tes cotisations URSSAF 2026 et ce qu’il te reste chaque mois.'),
]
NOTES = {
 'budget':'Le 50 / 30 / 20 est un repère, pas une règle. Avec un petit budget étudiant, les besoins prennent souvent plus de place.',
 'fractionne':'Un crédit vous engage et doit être remboursé. Vérifiez vos capacités de remboursement avant de vous engager.',
 'abonnements':'Ta liste reste enregistrée sur ton appareil uniquement.',
 'voiture':'Estimation. Le prix de l’assurance dépend beaucoup de ton âge, de ton bonus et de ta ville.',
 'appart':'Frais d’agence : maximum légal par m² selon la zone (8, 10 ou 12 €), plus 3 €/m² pour l’état des lieux. L’agence peut demander moins.',
 'coloc':'Une façon juste de partager parmi d’autres : mettez-vous d’accord avant de signer.',
 'salaire':'Estimation simplifiée. Les taux exacts dépendent de ta convention collective. Vérifie sur ta fiche de paie.',
 'interets':'Intérêts ajoutés chaque mois, taux constant. Dans la réalité un taux change, et en Bourse rien n’est garanti.',
 'livrets':'Taux au 1er août 2026 : Livret A et LDDS 1,7 %, LEP 2,5 %. Calcul simplifié (les intérêts réels se calculent par quinzaine).',
 'micro':'Taux URSSAF 2026 en métropole. L’ACRE peut réduire tes cotisations la première année : vérifie sur autoentrepreneur.urssaf.fr.',
}
def tool_icon(name):
    if name in ICONS: return ICONS[name]
    if name.startswith('Le vrai coût'): return ['#FCE6D8', CAR]
    return ['#E4ECFB', ICONS['Intérêts composés'][1]]
CATS = [('tous','Tous'),('appart','Mon appart'),('budget','Mon budget'),('job','Mon job'),('epargne','J’épargne'),('boite','Ma boîte')]

GUIDES = [
 ('investir-1000','Le plus lu','Investir tes premiers 1 000 €','Es-tu prêt, quelle enveloppe, 3 façons de faire comparées sur 2, 5 et 8 ans.','#E4ECFB',True),
 ('premier-appart','Logement','Louer ton premier appart','Garant, dépôt de garantie, APL, état des lieux : tout, dans l’ordre.','#ECE8FB',True),
 ('premiere-paie','Job','Ta première paie','Brut, net, impôts : comprendre ta fiche de paie et quoi faire des premiers euros.','#FCE6D8',True),
 ('erasmus','Erasmus','Partir en Erasmus','Bourses, budget sur place, banque à l’étranger.','#E4F4D2',False),
 ('micro-entreprise','Ma boîte','Lancer ta micro-entreprise','Créer, déclarer, payer tes cotisations sans stress.','#FFF1C9',False),
]

FICHES = [
 ('faire-un-budget','Budget','Débutant','Faire un budget en 10 minutes','#E4ECFB','🧾',
  ['<b>Un budget</b>, c’est ce qui rentre moins ce qui sort, chaque mois.','Note d’abord <b>ce qui rentre</b> : bourse, APL, job, aide des parents.','Puis <b>ce qui sort à coup sûr</b> : loyer, forfait, transport, abonnements.','Ce qui reste, c’est pour <b>manger, sortir et épargner</b>.','Repère simple : 50 % besoins, 30 % envies, 20 % épargne. Adapte-le à ta vie.'],
  ('Charges fixes','les dépenses qui reviennent tous les mois au même montant (loyer, forfait).'),'budget-du-mois'),
 ('les-apl','Logement','Débutant','Les APL, comment ça marche','#ECE8FB','🏠',
  ['<b>Les APL</b> sont une aide de la CAF pour payer ton loyer.','Tu fais la demande <b>sur le site de la CAF</b>, dès que tu as ton bail.','Le montant dépend de <b>ton loyer, ta ville et tes revenus</b>.','Elles sont souvent <b>versées directement au propriétaire</b> : ton loyer baisse d’autant.','Fais-la tout de suite : <b>pas de rattrapage</b> sur les mois passés.'],
  ('Bail','le contrat de location signé avec le propriétaire.'),'premier-appart'),
 ('le-livret-a','Épargne','Débutant','Le Livret A en 2 minutes','#FFF1C9','🐷',
  ['<b>Le Livret A</b> est un compte d’épargne : ton argent ne baisse jamais.','Il rapporte <b>1,7 % par an</b> depuis le 1er août 2026, sans impôt.','Tu peux retirer <b>quand tu veux</b>, sans frais.','Plafond : <b>22 950 €</b> de versements.','Idéal pour ton <b>épargne de secours</b> : 3 mois de dépenses de côté.'],
  ('Taux d’intérêt','ce que ton argent te rapporte en un an, en pourcentage.'),'comparateur-livrets'),
 ('lire-sa-fiche-de-paie','Job','Débutant','Lire ta fiche de paie','#FCE6D8','💶',
  ['<b>Le brut</b>, c’est ton salaire avant les cotisations.','<b>Les cotisations</b> financent ta santé, ton chômage et ta retraite.','<b>Le net</b>, c’est ce que tu touches vraiment sur ton compte.','Compte environ <b>22 % de différence</b> entre brut et net pour un salarié.','Garde toutes tes fiches de paie : elles servent <b>pour ta retraite</b>.'],
  ('Cotisations','l’argent prélevé sur ton salaire pour la protection sociale.'),'salaire-brut-net'),
 ('etf-c-est-quoi','Investir','Intermédiaire','Un ETF, c’est quoi ?','#E4F4D2','🧺',
  ['<b>Un ETF</b> (fonds indiciel) est un panier qui contient des centaines d’entreprises.','Il <b>copie un indice</b> : par exemple les grandes entreprises du monde.','Le risque est <b>réparti</b> : si une entreprise va mal, les autres compensent en partie.','Les frais sont souvent <b>bas</b>, mais compare-les toujours.','Il peut <b>baisser</b> : on parle de risque de perte en capital.'],
  ('Indice','une liste d’entreprises qui sert de mesure pour un marché, comme une moyenne.'),'interets-composes'),
 ('payer-en-plusieurs-fois','Crédit','Débutant','Le paiement en 3 ou 4 fois','#ECE8FB','💳',
  ['<b>Payer en plusieurs fois</b>, c’est un petit crédit, même sans en avoir l’air.','Depuis le 20 novembre 2026, c’est <b>encadré comme un crédit</b> à la consommation.','Il y a souvent <b>des frais</b> : regarde le coût total, pas la mensualité.','Plusieurs paiements en même temps, et <b>le budget explose</b> vite.','Règle d’or : si tu ne peux pas payer en une fois, demande-toi si tu en as besoin.'],
  ('Mensualité','la somme que tu paies chaque mois pour rembourser.'),'payer-en-3-ou-4-fois'),
]
THEMES = [('Budget','🧾',22,'#E4ECFB'),('Logement','🏠',18,'#ECE8FB'),('Job','💶',16,'#FCE6D8'),('Épargne','🐷',20,'#FFF1C9'),('Investir','📈',24,'#E4F4D2'),('Impôts','🧮',14,'#E4ECFB'),('Crédit','💳',12,'#ECE8FB'),('Ma boîte','🚀',15,'#FCE6D8')]

LEX = [
 ('Abattement','Une part de tes revenus que l’État ne compte pas pour calculer l’impôt.'),
 ('Action','Un petit morceau d’une entreprise. Sa valeur monte ou baisse.'),
 ('APL','Aide personnalisée au logement, versée par la CAF pour baisser ton loyer.'),
 ('Assurance habitation','Assurance qui couvre ton logement (dégât des eaux, incendie). Obligatoire pour un locataire.'),
 ('Assurance vie','Une enveloppe d’épargne avec des fonds sans risque et avec risque. Fiscalité allégée après 8 ans.'),
 ('Bail','Le contrat de location signé entre toi et le propriétaire.'),
 ('Brut','Ton salaire avant les cotisations sociales.'),
 ('Budget','Ce qui rentre moins ce qui sort, sur un mois.'),
 ('Capital','La somme de départ que tu places.'),
 ('Charges','Les frais en plus du loyer : eau, entretien de l’immeuble, parfois chauffage.'),
 ('Chiffre d’affaires','Tout l’argent encaissé par ton entreprise, avant de payer quoi que ce soit.'),
 ('Compte-titres','Une enveloppe où l’on peut acheter tout ce qui est coté en Bourse. Aucun avantage fiscal.'),
 ('Cotisations','L’argent prélevé pour financer santé, chômage et retraite.'),
 ('Crédit','De l’argent prêté que tu rembourses, souvent avec des intérêts.'),
 ('Dépôt de garantie','La somme versée au propriétaire à l’entrée, rendue à la sortie si tout va bien. 1 mois de loyer hors charges pour un logement vide, 2 mois maximum pour un meublé.'),
 ('Diversifier','Répartir son argent sur plusieurs placements pour réduire le risque.'),
 ('Enveloppe','Le compte qui « contient » tes placements, comme un dossier contient des fichiers.'),
 ('Épargne de secours','De l’argent de côté pour les imprévus, souvent 3 mois de dépenses.'),
 ('ETF','Un fonds indiciel : un panier de centaines d’entreprises qui copie un indice.'),
 ('Flat tax','Impôt unique sur les gains de placements : 31,4 % en 2026.'),
 ('Frais d’agence','Ce que l’agence immobilière te facture pour la location. Plafonné par la loi.'),
 ('Garant','Une personne qui s’engage à payer ton loyer si tu ne peux pas.'),
 ('Inflation','La hausse des prix : avec la même somme, tu achètes un peu moins chaque année.'),
 ('Intérêts composés','Tes intérêts rapportent eux aussi des intérêts. L’effet boule de neige.'),
 ('LDDS','Livret de développement durable et solidaire. Même taux que le Livret A, plafond 12 000 €.'),
 ('LEP','Livret d’épargne populaire, pour les revenus modestes. 2,5 % en 2026, plafond 10 000 €.'),
 ('Livret A','Compte d’épargne sans risque, 1,7 % par an depuis août 2026, plafond 22 950 €.'),
 ('Mensualité','La somme payée chaque mois pour rembourser un achat ou un crédit.'),
 ('Micro-entreprise','Le statut le plus simple pour se lancer seul : on paie des cotisations sur ce qu’on encaisse.'),
 ('Net','Ce que tu touches vraiment, après les cotisations.'),
 ('PEA','Plan d’épargne en actions. Après 5 ans, plus d’impôt sur le revenu sur les gains.'),
 ('Perte en capital','Le risque de récupérer moins que ce que tu as mis.'),
 ('Prélèvements sociaux','Contributions prélevées sur les gains de placements, en plus de l’impôt.'),
 ('Risque','La possibilité que la valeur de ton placement baisse.'),
 ('Taux d’intérêt','Ce que ton argent rapporte (ou ce que coûte un prêt) sur un an, en pourcentage.'),
 ('URSSAF','L’organisme qui collecte les cotisations sociales, notamment des micro-entrepreneurs.'),
 ('Versement libératoire','Option de la micro-entreprise : tu paies ton impôt en même temps que tes cotisations, en % de ton chiffre d’affaires.'),
]

# ---------- gabarit ----------
NAV = [('apprendre','Apprendre'),('outils','Outils'),('passer-a-l-action','Passer à l’action'),('lexique','Lexique'),('prix','Prix étudiant')]
def page(path, title, desc, body, section=None, script=False):
    nav = ''.join(f'<a href="/{k}/"{" aria-current=\"page\"" if section==k else ""}>{v}</a>' for k,v in NAV)
    url = DOMAIN + '/' + (path + '/' if path else '')
    full = title if path=='' else f'{title} – YouBiff'
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta name="theme-color" content="#F6F4EE">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="site-h">
  <div class="wrap">
    <a class="logo" href="/">You<span>Biff</span></a>
    <nav class="menu" aria-label="Menu principal">{nav}</nav>
    <a class="btn-dl" href="/telecharger/">Télécharger l’app</a>
    <button class="burger" type="button" aria-label="Ouvrir le menu" aria-expanded="false"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-f">
  <div class="wrap">
    <div class="cols">
      <div class="col"><a class="logo" href="/">You<span>Biff</span></a><span>L’app des étudiants, au prix étudiant.</span></div>
      <div class="col"><b>Produit</b><a href="/apprendre/">Apprendre</a><a href="/outils/">Outils</a><a href="/passer-a-l-action/">Passer à l’action</a><a href="/prix/">Prix étudiant</a></div>
      <div class="col"><b>Ressources</b><a href="/lexique/">Lexique</a><a href="/nouveautes/">Nouveautés de l’app</a><a href="/aide/">Aide et contact</a><a href="/a-propos/">À propos</a></div>
      <div class="col"><b>Légal</b><a href="/mentions-legales/">Mentions légales</a><a href="/conditions/">CGU et CGV</a><a href="/confidentialite/">Confidentialité</a></div>
    </div>
    <p class="legal">YouBiff est un service d’éducation financière. Il ne fournit aucun conseil en investissement et ne recommande aucun produit, courtier ou banque. Investir comporte un risque de perte en capital. Les calculs sont des estimations. © 2026 YouBiff · <a href="mailto:contact@youbiff.fr">contact@youbiff.fr</a></p>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''

def write(path, content):
    p = os.path.join(OUT, path, 'index.html') if path else os.path.join(OUT, 'index.html')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(content)
    PAGES.append(path)
PAGES = []

def sh(eyebrow, title, lead=''):
    return f'<div class="sh"><span class="eyebrow">{eyebrow}</span><h2 class="h2">{title}</h2>{f"<p class=lead>{lead}</p>" if lead else ""}</div>'
def tool_card(t, extra=''):
    bgc, svg = tool_icon(t[2])
    return f'<a class="tool-c" href="/outils/{t[0]}/"{extra}><span class="ic" style="background: {bgc}">{svg}</span><span class="t">{t[2]}</span><span class="d">{t[3]}</span><span class="m">Calculer →</span></a>'
def guide_card(g):
    href = f'/passer-a-l-action/{g[0]}/' if g[5] else '/passer-a-l-action/#bientot'
    return f'<a class="guide-c" href="{href}" style="background: {g[4]}"><span class="tag{"" if g[5] else " soft"}">{g[1] if g[5] else g[1]+" · bientôt"}</span><span class="t">{g[2]}</span><span class="d">{g[3]}</span><span class="m">{"Suivre le guide →" if g[5] else "Bientôt disponible"}</span></a>'
def dl_btn(): return f'<a class="btn-ink" href="/telecharger/">{APPLE}Bientôt sur l’App Store</a>'
def pagehead(eyebrow, title, lead, crumb=''):
    return f'<section class="pagehead"><div class="wrap">{crumb}<div class="sh" style="gap:14px"><span class="eyebrow">{eyebrow}</span><h1 class="hero-t">{title}</h1>{f"<p class=lead>{lead}</p>" if lead else ""}</div></div></section>'
def crumb(*parts):
    out=[]
    for href,label in parts:
        out.append(f'<a href="{href}">{label}</a>' if href else label)
    return '<nav class="crumb" aria-label="Fil d’Ariane">'+' › '.join(out)+'</nav>'
def price_block(head=True):
    return f'''<div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px">
  <div class="price"><span class="n">Premium · mensuel</span><span class="a">{PRIX}</span><span class="s">par mois, sans engagement</span></div>
  <div class="price lime"><span class="n">Gratuit · pour toujours</span><span class="a">0 €</span><span class="s">leçons Débutant, 10 outils, 1 partie de jeu par jour</span></div>
</div>'''
FAQ = [
 ('Est-ce que YouBiff me dit où placer mon argent ?','Non. YouBiff t’explique comment ça marche pour que tu décides toi-même. On ne recommande jamais de produit, de banque ou de courtier.'),
 ('C’est vraiment pour les étudiants ?','Oui : APL, bourse, job, alternance, coloc, premier appart. Les exemples parlent de ta vie, pas de celle d’un cadre de 45 ans.'),
 ('Qu’est-ce qui est gratuit ?','Les leçons Débutant de tous les thèmes, les 10 outils et une partie de jeu par jour. Pour toujours.'),
 ('Faut-il créer un compte ?','Non pour commencer. Tu peux en créer un plus tard pour sauvegarder ta progression et défier tes amis.'),
]
def faq(items, first_open=True):
    return ''.join(f'<details class="q"{" open" if (i==0 and first_open) else ""}><summary>{q}</summary><p>{a}</p></details>' for i,(q,a) in enumerate(items))

# ---------- ACCUEIL (maquette) ----------
def home():
    phone = f'''<div class="phone hide-m" aria-hidden="true"><div class="in">
    <div style="display: flex; justify-content: space-between; align-items: center"><span style="font-size: 14px; font-weight: 800">Salut Sam</span><span style="display: inline-flex; align-items: center; gap: 4px; padding: 5px 9px; border-radius: 999px; background: #FFFFFF; font-size: 12px; font-weight: 800">{FLAME} 12 j</span></div>
    <div style="background: #0B7F58; border-radius: 18px; padding: 14px; color: #FFFFFF; display: flex; flex-direction: column; gap: 8px"><span style="font-size: 10px; font-weight: 800; letter-spacing: 0.08em">REPRENDRE · INVESTIR</span><span style="font-size: 16px; font-weight: 800">Les ETF, c’est quoi ?</span><span style="height: 6px; border-radius: 9px; background: rgba(255,255,255,0.25)"><span style="display: block; width: 40%; height: 6px; border-radius: 9px; background: #C8F27A"></span></span></div>
    <div style="background: #FFFFFF; border-radius: 14px; padding: 10px 12px; font-size: 12px; font-weight: 800">Défis du jour 2/4</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px">{''.join(f'<span style="height: 70px; border-radius: 14px; background: #FFFFFF; display:flex; flex-direction:column; justify-content:center; padding:0 12px; font-size:12px; font-weight:800"><span style="font-size:20px">{e}</span>{n}</span>' for n,e,_,_ in THEMES[:4])}</div>
    <div style="margin-top: auto; height: 42px; border-radius: 14px; background: #FFF1C9; display:flex; align-items:center; padding:0 12px; font-size:12px; font-weight:800">Mot du jour : Livret A</div>
  </div></div>'''
    body = f'''<section class="hero"><div class="wrap">
    <div style="flex: 1; min-width: 300px; display: flex; flex-direction: column; gap: 22px">
      <span class="pill">100 % pensé pour les étudiants</span>
      <h1 class="hero-t">Ton argent,<br>enfin <span class="hl">compris.</span></h1>
      <p style="margin: 0; font-size: 19px; line-height: 1.55; color: #4E5468; max-width: 520px">Budget, appart, job, épargne, Bourse : des fiches claires, des jeux et des outils gratuits. Cinq minutes par jour, sans jargon.</p>
      <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center">{dl_btn()}<a class="link-b" href="/outils/">Essayer un outil gratuit →</a></div>
    </div>
    {phone}
</div></section>
<section style="padding: 8px 0 64px"><div class="wrap grid g-stats">
  <div class="stat"><b>141</b><span>leçons en fiches</span></div>
  <div class="stat"><b>10</b><span>outils gratuits, aussi sur le web</span></div>
  <div class="stat"><b>5 min</b><span>par jour suffisent</span></div>
  <div class="stat lime"><b>{PRIX}</b><span>par mois, sans engagement</span></div>
</div></section>
<section class="sec white"><div class="wrap stack">
  {sh('Passer à l’action','Les questions que tu te poses vraiment','Des guides interactifs : tu entres tes chiffres, on t’explique chaque étape. Jamais de produit à acheter.')}
  <div class="grid g-guides">{''.join(guide_card(g) for g in GUIDES[:3])}</div>
</div></section>
<section class="sec"><div class="wrap stack">
  <div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap">{sh('Outils','10 calculateurs, sans compte')}<a class="link-b" href="/outils/">Voir les 10 calculs →</a></div>
  <div class="grid g-tools">{''.join(tool_card(t) for t in [TOOLS[i] for i in (4,5,0,1,2,6,9,8)])}</div>
</div></section>
<section class="sec green"><div class="wrap" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; align-items: center">
  {sh('Notre méthode','Apprendre comme en cours, mais en mieux','Toutes les leçons sont des fiches : l’essentiel, illustré, que tu relis en deux minutes.')}
  <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px">
    <div class="mini"><b>Des fiches, pas des pavés</b><span>L’essentiel en phrases courtes et en dessins.</span></div>
    <div class="mini"><b>Zéro jargon</b><span>Chaque mot nouveau est expliqué avant d’être utilisé.</span></div>
    <div class="mini"><b>Indépendant</b><span>Aucune banque, aucun courtier, aucune pub.</span></div>
    <div class="mini"><b>Chiffres vérifiés</b><span>Sources officielles, datées, mises à jour.</span></div>
  </div>
</div></section>
<section class="sec"><div class="wrap" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; align-items: start">
  {sh('Prix','L’app des étudiants, au prix étudiant','Un prix simple, sans surprise. Tu résilies en deux clics.')}
  <div style="display: flex; flex-direction: column; gap: 14px">{price_block()}<span style="font-size: 14px; color: #5B6175">Pas d’essai piège, pas de pièces à acheter : un seul prix, c’est tout.</span></div>
</div></section>
<section class="sec white"><div class="wrap" style="display: flex; flex-direction: column; gap: 24px; max-width: 860px">
  {sh('Questions','Tu te demandes peut-être')}
  {faq(FAQ)}
</div></section>
<section style="padding: 88px 0"><div class="wrap" style="display: flex; flex-direction: column; align-items: center; gap: 22px; text-align: center">
  <h2 style="margin: 0; font-size: 48px; line-height: 1.05; font-weight: 800; letter-spacing: -0.04em; max-width: 760px" class="h2">L’école ne t’a pas appris l’argent. <span class="hl">YouBiff, si.</span></h2>
  {dl_btn()}
</div></section>'''
    write('', page('', 'YouBiff : comprendre l’argent quand on est étudiant', 'Budget, appart, job, épargne, Bourse : des fiches claires, 10 outils gratuits et des guides pas à pas. Sans jargon, sans pub, au prix étudiant.', body))

# ---------- OUTILS ----------
def outils():
    chips = ''.join(f'<button type="button" class="chip" data-cat="{k}" aria-pressed="{str(k=="tous").lower()}">{v}</button>' for k,v in CATS)
    body = pagehead('Outils','10 calculs gratuits, sans compte','Tu entres tes chiffres, tu as la réponse tout de suite. Rien n’est envoyé : tout reste sur ton appareil.') + f'''
<section style="padding: 32px 0 80px"><div class="wrap stack" style="gap:24px">
  <div class="chips" role="group" aria-label="Filtrer les outils">{chips}</div>
  <div class="grid g-tools">{''.join(tool_card(t, f' data-cats="{t[4]}"') for t in TOOLS)}</div>
</div></section>'''
    write('outils', page('outils','10 calculateurs gratuits pour étudiants','Budget, premier appart, coloc, salaire brut en net, livrets, micro-entreprise : 10 calculateurs gratuits, sans compte.', body, 'outils'))
    for t in TOOLS:
        others = [x for x in TOOLS if x[4]==t[4] and x!=t] + [x for x in TOOLS if x[4]!=t[4]]
        body = f'''<section style="padding: 40px 0 0"><div class="wrap">
  {crumb(('/outils/','Outils'),(None,t[2]))}
  <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><span class="tool-c" style="padding:0;border:0;background:none"><span class="ic" style="width:60px;height:60px;border-radius:16px;background:{tool_icon(t[2])[0]}">{tool_icon(t[2])[1]}</span></span><div><h1 class="hero-t" style="margin:0;font-size:48px;line-height:1.05;font-weight:800;letter-spacing:-0.04em">{t[2]}</h1><p class="lead" style="margin-top:6px">{t[5]}</p></div></div>
  <div class="tool-l" data-tool="{t[1]}">
    <div class="form"><form id="tf" onsubmit="return false"><noscript><p>Active JavaScript pour utiliser le calculateur.</p></noscript></form><p class="small" style="margin:4px 0 14px">{NOTES[t[1]]}</p><div class="acts"><button type="button" class="btn-light" id="copy">Copier le résultat</button><button type="button" class="btn-light" id="reset">Remettre à zéro</button></div></div>
    <div class="res" aria-live="polite"><span class="eyebrow" id="r-eye"></span><span class="tot" id="r-tot">–</span><p class="sub" id="r-sub"></p><div class="lines" id="r-lines"></div><div id="r-extra"></div></div>
  </div>
</div></section>
<section class="sec"><div class="wrap stack">
  {sh('Continuer','D’autres calculs utiles')}
  <div class="grid g-tools">{''.join(tool_card(x) for x in others[:4])}</div>
</div></section>'''
        write(f'outils/{t[0]}', page(f'outils/{t[0]}', f'{t[2]} : calculateur gratuit', t[5], body, 'outils'))

# ---------- APPRENDRE ----------
def apprendre():
    themes = ''.join(f'<div class="theme"><span class="e" style="background:{c}" aria-hidden="true">{e}</span><span><b>{n}</b><span>{k} fiches</span></span></div>' for n,e,k,c in THEMES)
    cards = ''.join(f'<a class="fc" href="/apprendre/{f[0]}/"><span class="il" style="background:{f[4]}" aria-hidden="true">{f[5]}</span><span class="tag soft">{f[1]} · {f[2]}</span><span class="t">{f[3]}</span><span class="m">Lire la fiche →</span></a>' for f in FICHES)
    body = pagehead('Apprendre','Des fiches qu’on lit en 2 minutes','Chaque thème va du niveau Débutant au niveau Expert. Les fiches Débutant sont gratuites, dans l’app. En voici quelques-unes à lire tout de suite.') + f'''
<section style="padding: 40px 0 24px"><div class="wrap stack" style="gap:20px">{sh('Les thèmes','8 thèmes, 141 fiches')}<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px">{themes}</div></div></section>
<section class="sec"><div class="wrap stack" style="gap:20px">{sh('À lire maintenant','Six fiches pour commencer')}<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px">{cards}</div></div></section>'''
    write('apprendre', page('apprendre','Apprendre l’argent en fiches','Budget, logement, job, épargne, investir, impôts : des fiches courtes et illustrées pour comprendre l’argent quand on est étudiant.', body, 'apprendre'))
    for i,f in enumerate(FICHES):
        nx = FICHES[(i+1)%len(FICHES)]
        t = next(x for x in TOOLS if x[0]==f[8])
        body = f'''<section style="padding: 40px 0 80px"><div class="wrap">
  {crumb(('/apprendre/','Apprendre'),(None,f[1]))}
  <article class="fiche">
    <div class="illu" style="background:{f[4]}" aria-hidden="true">{f[5]}</div>
    <span class="tag soft">{f[1]} · {f[2]} · 2 min</span>
    <h1>{f[3]}</h1>
    <ul>{''.join('<li>'+p+'</li>' for p in f[6])}</ul>
    <div class="mot"><span class="k">Mot nouveau</span><span><b>{f[7][0]}</b> : {f[7][1]}</span></div>
    <div class="acts"><a class="btn-green" href="/apprendre/{nx[0]}/">Fiche suivante →</a><a class="btn-light" href="/outils/{t[0]}/">Calculer : {t[2]}</a></div>
  </article>
</div></section>'''
        plain = re.sub('<[^>]+>','',f[6][0])
        write(f'apprendre/{f[0]}', page(f'apprendre/{f[0]}', f[3], plain+' Une fiche YouBiff à lire en 2 minutes.', body, 'apprendre'))

# ---------- PASSER À L'ACTION ----------
def guides():
    body = pagehead('Passer à l’action','Des guides pas à pas','Pour les grandes premières fois : investir, louer, être payé. Tu avances étape par étape et tu décides toi-même.') + f'''
<section style="padding: 36px 0 80px"><div class="wrap stack"><div class="grid g-guides">{''.join(guide_card(g) for g in GUIDES)}</div>
<p id="bientot" class="small">Les guides « bientôt » sont en cours d’écriture : on vérifie chaque chiffre avant de les publier.</p></div></section>'''
    write('passer-a-l-action', page('passer-a-l-action','Guides pas à pas pour étudiants','Investir tes premiers 1 000 €, louer ton premier appart, ta première paie : des guides clairs, étape par étape, sans produit à vendre.', body, 'passer-a-l-action'))

    # Guide 1000 € (maquette SiteGuide)
    steps = ['Es-tu prêt ?','Choisir où ranger ton argent','Ce que tu peux acheter','3 façons comparées','Les erreurs à éviter']
    toc = ''.join(f'<a href="#e{i+1}"><span>{i+1}</span><span>{s}</span></a>' for i,s in enumerate(steps))
    h2 = lambda i: f'<h2 id="e{i}"><span class="num">{i}</span>{steps[i-1]}</h2>'
    qs = ['As-tu de côté de quoi tenir 3 mois de dépenses ?','As-tu fini de rembourser tes crédits à la consommation ?','Pourras-tu laisser cet argent au moins 5 ans ?']
    yn = ''.join(f'<div class="yn"><span>{q}</span><span class="choice" role="group" aria-label="{q}"><button type="button" data-v="1" aria-pressed="false">Oui</button><button type="button" data-v="0" aria-pressed="false">Non</button></span></div>' for q in qs)
    body = f'''<section style="padding: 40px 0 0"><div class="wrap">
  {crumb(('/passer-a-l-action/','Passer à l’action'),(None,'Investir'))}
  <div style="display: flex; flex-direction: column; gap: 16px; max-width: 820px">
    <span class="tag" style="font-size:13px;padding:6px 11px">Guide interactif · 6 min</span>
    <h1 class="hero-t" style="margin: 0; font-size: 54px; line-height: 1.05; font-weight: 800; letter-spacing: -0.04em">Investir tes premiers 1 000 € quand tu es étudiant</h1>
    <p style="margin: 0; font-size: 19px; line-height: 1.55; color: #4E5468">5 étapes pour comprendre avant d’agir. Tu réponds, tu compares, tu décides toi-même : on ne te dira jamais quoi acheter.</p>
    <span style="font-size: 14px; color: #5B6175">Mis à jour le {MAJ}</span>
  </div>
  <div class="guide-l" id="guide1000">
    <aside class="toc-a"><nav class="toc" aria-label="Sommaire"><span class="ttl">Sommaire</span>{toc}</nav>
      <div class="cta-g"><b>Fais-le avec tes chiffres</b><span>Le guide complet sera dans l’app, avec ton portefeuille simulé.</span><a class="btn-green" href="/telecharger/">Bientôt dans l’app</a></div></aside>
    <article class="art">
      {h2(1)}
      <p>Avant de penser Bourse, trois vérifications. Elles reprennent les conseils de l’AMF, le gendarme de la Bourse.</p>
      {yn}
      <p class="note-g" id="verdict" aria-live="polite">Réponds aux 3 questions pour voir où tu en es.</p>
      {h2(2)}
      <p>Avant d’acheter quoi que ce soit, il faut une « enveloppe » : le compte qui contient tes placements. Elle change surtout les impôts.</p>
      <div class="tbl"><table><thead><tr><th scope="col">Enveloppe</th><th scope="col">Ce qu’on peut y mettre</th><th scope="col">Impôts sur les gains</th><th scope="col">À savoir</th></tr></thead><tbody>
        <tr><th scope="row">PEA</th><td>Actions européennes et fonds qui en contiennent</td><td>Plus d’impôt sur le revenu après 5 ans (prélèvements sociaux restent)</td><td>Plafond de 150 000 € de versements</td></tr>
        <tr><th scope="row">Compte-titres</th><td>Tout ce qui est coté</td><td>Flat tax de 31,4 % sur les gains (2026)</td><td>Aucun plafond, aucun avantage</td></tr>
        <tr><th scope="row">Assurance vie</th><td>Fonds en euros et fonds en unités de compte</td><td>Allégés après 8 ans</td><td>On peut y mettre de l’argent sans risque et avec risque</td></tr>
      </tbody></table></div>
      <div class="mot"><span class="k">Mot nouveau</span><span><b>Enveloppe</b> : le compte qui « contient » tes placements, comme un dossier contient des fichiers.</span></div>
      {h2(3)}
      <ul><li><b>Un livret</b> : ton argent ne baisse jamais, mais il grandit lentement.</li><li><b>Une action</b> : un petit morceau d’une seule entreprise. Si elle va mal, tu perds.</li><li><b>Un fonds indiciel (ETF)</b> : un panier de centaines d’entreprises d’un coup. Le risque est réparti.</li></ul>
      {h2(4)}
      <p>Voici ce que pourraient devenir <b id="g-txt">1 000 € en 8 ans</b>, selon la façon de les placer. Change la durée pour voir le risque grandir quand le temps raccourcit.</p>
      <div style="display:flex;gap:14px;flex-wrap:wrap;align-items:flex-end">
        <div class="field" style="margin:0;width:200px"><label for="g-mt">Montant</label><div class="inp"><input id="g-mt" inputmode="decimal" value="1000"><span>€</span></div></div>
        <div class="field" style="margin:0"><span class="lb" id="g-dur-l">Durée</span><span class="choice" id="g-dur" role="group" aria-labelledby="g-dur-l"><button type="button" data-v="2" aria-pressed="false">2 ans</button><button type="button" data-v="5" aria-pressed="false">5 ans</button><button type="button" data-v="8" aria-pressed="true">8 ans</button></span></div>
      </div>
      <div id="ways" style="display:flex;flex-direction:column;gap:12px"></div>
      <span class="small">Hypothèses d’exemple : livret à 1,7 % par an, actions monde à 6 % par an en moyenne. Les performances passées ne préjugent pas des performances futures. Investir en Bourse comporte un risque de perte en capital.</span>
      {h2(5)}
      <ul><li>Investir l’argent dont tu auras besoin l’an prochain.</li><li>Tout miser sur une seule entreprise parce qu’elle est à la mode.</li><li>Vendre en panique quand ça baisse.</li><li>Oublier les frais : 1 % de frais par an, ça pèse lourd sur 20 ans.</li><li>Croire une promesse de gain rapide : c’est souvent une arnaque. Vérifie les listes noires de l’AMF.</li></ul>
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px">{tool_card(TOOLS[8])}{tool_card(TOOLS[7])}</div>
    </article>
  </div>
</div></section>'''
    write('passer-a-l-action/investir-1000', page('passer-a-l-action/investir-1000','Investir tes premiers 1 000 € quand tu es étudiant','Es-tu prêt, quelle enveloppe choisir (PEA, compte-titres, assurance vie), 3 façons de placer 1 000 € comparées sur 2, 5 et 8 ans. Sans produit à vendre.', body, 'passer-a-l-action'))

    def simple(slug, tag, title, lead, desc, steps):
        toc = ''.join(f'<a href="#e{i+1}"><span>{i+1}</span><span>{s[0]}</span></a>' for i,s in enumerate(steps))
        art = ''.join(f'<h2 id="e{i+1}"><span class="num">{i+1}</span>{s[0]}</h2>{s[1]}' for i,s in enumerate(steps))
        body = f'''<section style="padding: 40px 0 0"><div class="wrap">
  {crumb(('/passer-a-l-action/','Passer à l’action'),(None,tag))}
  <div style="display:flex;flex-direction:column;gap:16px;max-width:820px"><span class="tag" style="font-size:13px;padding:6px 11px">Guide pas à pas</span><h1 class="hero-t" style="margin:0;font-size:54px;line-height:1.05;font-weight:800;letter-spacing:-0.04em">{title}</h1><p style="margin:0;font-size:19px;line-height:1.55;color:#4E5468">{lead}</p><span style="font-size:14px;color:#5B6175">Mis à jour le {MAJ}. Informations générales, à vérifier selon ta situation.</span></div>
  <div class="guide-l"><aside class="toc-a"><nav class="toc" aria-label="Sommaire"><span class="ttl">Sommaire</span>{toc}</nav></aside><article class="art">{art}</article></div>
</div></section>'''
        write(f'passer-a-l-action/{slug}', page(f'passer-a-l-action/{slug}', title, desc, body, 'passer-a-l-action'))
    simple('premier-appart','Logement','Louer ton premier appart','Les étapes dans l’ordre, de la recherche à la remise des clés.','Budget, dossier, garant, dépôt de garantie, frais d’agence, état des lieux, APL : louer ton premier appart étape par étape.',[
     ('Fixer ton budget','<ul><li>Vise un loyer charges comprises <b>autour d’un tiers de tes revenus</b>, APL comprises.</li><li>Compte aussi l’électricité, internet et l’assurance habitation.</li></ul>'),
     ('Préparer ton dossier','<ul><li>Pièce d’identité, carte étudiante, justificatifs de revenus ou de bourse.</li><li>Un <b>garant</b> : un proche, ou la garantie Visale (gratuite, demande sur visale.fr).</li></ul>'),
     ('Payer l’entrée','<ul><li><b>Dépôt de garantie</b> : 1 mois de loyer hors charges pour un logement vide, 2 mois maximum pour un meublé.</li><li><b>Frais d’agence</b> : plafonnés au m² par la loi, selon la ville.</li><li>Le premier loyer et l’assurance habitation.</li></ul><p><a class="btn-green" href="/outils/premier-appart/">Calculer mon entrée →</a></p>'),
     ('Faire l’état des lieux','<ul><li>Note <b>chaque défaut</b> et prends des photos datées.</li><li>C’est ce document qui protège ton dépôt de garantie à la sortie.</li></ul>'),
     ('Demander les APL','<ul><li>Dès la signature du bail, sur le site de la CAF.</li><li><b>Pas de rattrapage</b> sur les mois passés : ne traîne pas.</li></ul>')])
    simple('premiere-paie','Job','Ta première paie','Comprendre ce que tu touches et quoi en faire.','Brut, net, impôt à la source, fiches de paie : comprendre ta première paie de job étudiant, stage ou alternance.',[
     ('Brut et net','<ul><li><b>Brut</b> : le salaire avant cotisations. <b>Net</b> : ce qui arrive sur ton compte.</li><li>Environ <b>22 %</b> d’écart pour un salarié non cadre.</li></ul><p><a class="btn-green" href="/outils/salaire-brut-net/">Calculer mon net →</a></p>'),
     ('L’impôt à la source','<ul><li>L’impôt peut être prélevé directement sur ta paie.</li><li>Étudiant de moins de 26 ans : tes salaires sont exonérés <b>jusqu’à un plafond</b> (3 fois le SMIC mensuel par an). Vérifie sur impots.gouv.fr.</li></ul>'),
     ('Garder tes fiches de paie','<ul><li>Elles prouvent tes droits à la retraite et au chômage.</li><li>Garde-les dans un dossier, papier ou numérique, <b>sans limite de temps</b>.</li></ul>'),
     ('Quoi faire des premiers euros','<ul><li>D’abord une <b>épargne de secours</b> sur un livret.</li><li>Ensuite seulement, des projets plus longs.</li></ul><p><a class="btn-light" href="/outils/budget-du-mois/">Faire mon budget →</a></p>')])

# ---------- LEXIQUE ----------
def lexique():
    out=''; L=''
    import unicodedata
    for w,d in LEX:
        l = unicodedata.normalize('NFD', w[0]).upper()[0]
        if l != L: L=l; out += f'<div class="letter">{l}</div>'
        out += f'<div class="word" id="{re.sub("[^a-z0-9]+","-",unicodedata.normalize("NFD",w.lower()).encode("ascii","ignore").decode()).strip("-")}"><b>{w}</b><p>{d}</p></div>'
    body = pagehead('Lexique','Les mots de l’argent, en clair',f'{len(LEX)} mots expliqués en une phrase. Tape un mot pour le trouver.') + f'''
<section style="padding: 28px 0 80px"><div class="wrap" style="max-width:860px">
  <div class="inp search"><input id="lexq" type="search" placeholder="Ex. : flat tax, APL, ETF…" aria-label="Chercher un mot"></div>
  <div>{out}</div><p id="lexnone" class="small" hidden>Aucun mot trouvé. Essaie un autre mot.</p>
</div></section>'''
    write('lexique', page('lexique','Lexique de l’argent pour étudiants','APL, flat tax, ETF, LEP, dépôt de garantie : les mots de l’argent expliqués simplement, en une phrase.', body, 'lexique'))

# ---------- PRIX, TÉLÉCHARGER, AIDE, NOUVEAUTÉS ----------
def misc():
    body = pagehead('Prix étudiant','L’app des étudiants, au prix étudiant','Un prix simple, sans surprise. Tu résilies en deux clics depuis ton iPhone.') + f'''
<section style="padding: 36px 0 24px"><div class="wrap" style="max-width:860px">{price_block()}</div></section>
<section class="sec"><div class="wrap grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
  <div class="mini" style="border:1px solid #E3DFD5"><b>Pas d’essai piège</b><span>Pas d’essai gratuit qui se transforme en abonnement sans prévenir.</span></div>
  <div class="mini" style="border:1px solid #E3DFD5"><b>Pas de pièces à acheter</b><span>Aucune monnaie virtuelle, aucun pack. Un seul prix, c’est tout.</span></div>
  <div class="mini" style="border:1px solid #E3DFD5"><b>Résiliable en 2 clics</b><span>Réglages de l’iPhone › ton nom › Abonnements › YouBiff.</span></div>
</div></section>
<section class="sec white"><div class="wrap" style="display:flex;flex-direction:column;gap:24px;max-width:860px">{sh('Questions','Sur l’abonnement')}{faq([
 ('Qu’est-ce que Premium ajoute ?','Les fiches Intermédiaire et Expert de tous les thèmes, les parties de jeu sans limite et les guides complets dans l’app.'),
 ('Comment je paie ?','Sur iPhone, l’abonnement est payé et géré par Apple. YouBiff ne voit jamais tes informations de paiement.'),
 ('Comment je résilie ?','Réglages de l’iPhone › ton nom › Abonnements › YouBiff › Annuler. Tu gardes l’accès jusqu’à la fin du mois payé.')])}</div></section>'''
    write('prix', page('prix','Prix étudiant','YouBiff Premium : '+PRIX+' par mois, sans engagement. Les leçons Débutant, les 10 outils et 1 partie de jeu par jour restent gratuits.', body, 'prix'))

    body = f'''<section style="padding: 88px 0"><div class="wrap" style="display:flex;flex-direction:column;align-items:center;gap:22px;text-align:center">
  <span class="pill">L’app iPhone</span>
  <h1 class="hero-t" style="margin:0;font-size:54px;line-height:1.05;font-weight:800;letter-spacing:-0.04em;max-width:760px">YouBiff arrive bientôt sur l’App Store</h1>
  <p class="lead">L’app est en test. En attendant, les 10 outils et les guides sont déjà gratuits ici, sur le site.</p>
  <div class="acts" style="justify-content:center"><a class="btn-green" href="/outils/">Essayer les outils</a><a class="btn-light" href="/passer-a-l-action/investir-1000/">Lire le guide 1 000 €</a></div>
</div></section>'''
    write('telecharger', page('telecharger','Télécharger l’app','L’app YouBiff arrive bientôt sur l’App Store. Les outils et les guides sont déjà gratuits sur le site.', body))

    body = pagehead('Aide','Besoin d’aide ?','Une question, un souci avec ton compte ou ton abonnement ? Écris-nous, on te répond.') + f'''
<section style="padding: 32px 0 80px"><div class="wrap" style="max-width:860px;display:flex;flex-direction:column;gap:16px">
  <div class="box" style="display:flex;flex-direction:column;gap:8px"><b style="font-size:18px">Nous écrire</b><a href="mailto:contact@youbiff.fr" style="font-size:20px;font-weight:800">contact@youbiff.fr</a><span class="small">On répond en général sous 48 heures.</span></div>
  {faq([
   ('Comment supprimer mon compte ?','Dans l’app : onglet Profil › Mon compte › Supprimer mon compte. Ton compte et tes progrès en ligne sont effacés tout de suite et définitivement. Tu peux aussi nous le demander par e-mail.'),
   ('Comment résilier mon abonnement ?','Réglages de l’iPhone › ton nom › Abonnements › YouBiff › Annuler. Tu gardes l’accès jusqu’à la fin de la période payée.'),
   ('Comment me faire rembourser ?','Les achats faits sur l’App Store sont remboursés par Apple : va sur reportaproblem.apple.com.'),
   ('J’ai perdu ma progression','Si tu avais créé un compte, reconnecte-toi avec la même adresse : ta progression revient. Sans compte, elle est enregistrée seulement sur ton téléphone.'),
   ('J’ai trouvé une erreur dans une leçon','Merci ! Écris-nous à contact@youbiff.fr avec le nom de la leçon : on corrige vite.')], first_open=False)}
</div></section>'''
    write('aide', page('aide','Aide et contact','Contacter YouBiff, supprimer ton compte, résilier ton abonnement, demander un remboursement.', body))

    body = pagehead('Nouveautés','Ce qui change dans YouBiff','Chaque mise à jour, en phrases simples.') + f'''
<section style="padding: 32px 0 80px"><div class="wrap" style="max-width:860px;display:flex;flex-direction:column;gap:16px">
  <div class="box"><span class="tag">Site · {MAJ}</span><h2 style="margin:12px 0 8px;font-size:22px">Le nouveau site est en ligne</h2><ul style="margin:0;padding-left:20px;color:#4E5468;line-height:1.7"><li>Les 10 outils sont gratuits sur le web, chacun avec sa page.</li><li>Nouveau guide : investir tes premiers 1 000 €.</li><li>Un lexique de {len(LEX)} mots, avec recherche.</li></ul></div>
</div></section>'''
    write('nouveautes', page('nouveautes','Nouveautés','Les nouveautés de l’app et du site YouBiff.', body))

    body = f'''<section style="padding: 88px 0"><div class="wrap" style="display:flex;flex-direction:column;align-items:center;gap:18px;text-align:center"><h1 class="hero-t" style="margin:0;font-size:54px;font-weight:800;letter-spacing:-0.04em">Page introuvable</h1><p class="lead">Cette page n’existe pas ou a déménagé.</p><div class="acts" style="justify-content:center"><a class="btn-green" href="/">Retour à l’accueil</a><a class="btn-light" href="/outils/">Voir les outils</a></div></div></section>'''
    open(os.path.join(OUT,'404.html'),'w').write(page('404','Page introuvable','Page introuvable.', body))

# ---------- PAGES LÉGALES (texte d'origine, nouveau design) ----------
def legal():
    for slug in ['mentions-legales','confidentialite','conditions','a-propos']:
        s = open(os.path.join(SRC, slug, 'index.html')).read()
        m = s[s.find('<main'):s.find('</main>')]
        h1 = re.search(r'<h1>(.*?)</h1>', m, re.S).group(1)
        resume = re.search(r'<p class="resume">(.*?)</p>', m, re.S)
        resume = resume.group(1) if resume else ''
        parts = re.split(r'<h2>(.*?)</h2>', m)
        secs = ''
        for i in range(1, len(parts), 2):
            content = parts[i+1].strip()
            secs += f'<section><h2>{parts[i]}</h2>{content}</section>'
        if slug == 'conditions':
            secs = secs.replace('Abonnement mensuel : 4,99 € par mois. Abonnement annuel : 29,99 € par an.', f'Abonnement mensuel : {PRIX} par mois.')
            assert PRIX in secs, 'prix non remplacé dans les conditions'
            resume = resume.replace('2 novembre 2026', MAJ); secs = secs.replace('Dernière mise à jour : 2 novembre 2026', 'Dernière mise à jour : '+MAJ)
        if slug == 'confidentialite':
            secs = secs.replace('Pas de cookie publicitaire ni de mesure d’audience.', 'Les calculateurs du site fonctionnent dans ton navigateur : les chiffres que tu tapes ne nous sont pas envoyés. Pas de cookie publicitaire ni de mesure d’audience.')
        secs = secs.replace('<p>', '<p>').replace('href="/', 'href="/')
        title_plain = re.sub('<[^>]+>','',h1)
        body = f'''<section class="pagehead"><div class="wrap"><div class="sh" style="gap:14px"><span class="eyebrow">{"À propos" if slug=="a-propos" else "Légal"}</span><h1 class="hero-t">{h1}</h1><p class="lead">{resume}</p></div></div></section>
<div class="wrap"><div class="legalpage">{secs}</div></div>'''
        write(slug, page(slug, title_plain, re.sub('<[^>]+>','',resume) or title_plain, body))

# ---------- divers ----------
def extras():
    os.makedirs(os.path.join(OUT,'assets'), exist_ok=True)
    shutil.copy(os.path.join(B,'site.css'), os.path.join(OUT,'assets','site.css'))
    shutil.copy(os.path.join(B,'site.js'), os.path.join(OUT,'assets','site.js'))
    open(os.path.join(OUT,'assets','favicon.svg'),'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#0B7F58"/><text x="32" y="44" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" font-weight="800" fill="#C8F27A">Y</text></svg>')
    open(os.path.join(OUT,'CNAME'),'w').write('youbiff.fr\n')
    open(os.path.join(OUT,'.nojekyll'),'w').write('')
    open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    urls = ''.join(f'<url><loc>{DOMAIN}/{p+"/" if p else ""}</loc></url>' for p in PAGES)
    open(os.path.join(OUT,'sitemap.xml'),'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')

if __name__ == '__main__':
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    home(); outils(); apprendre(); guides(); lexique(); misc(); legal(); extras()
    print(len(PAGES), 'pages ->', OUT)
