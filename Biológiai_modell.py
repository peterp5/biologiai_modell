import pygame
import random
import math
import copy
from collections import Counter
import pygame_textinput


####################################################################################################
############################################ HÁTTÉR ################################################
####################################################################################################


########################################### VÁLTOZÓK ###############################################

# Mező

meret = 14  # egy állat mérete (négyzet oldalhossza)
szel = 50  # a mező szélessége
mag = 40  # a mező magassága
szinek = {'r': (187, 121, 0), 'n': (119, 119, 119), 'f': (80, 180, 80)}  # különböző területek színei

# Teljes kép

diaSzel = 30*meret  # diagram szélessége (összes rendelkezésre álló hely)
gyors = 10  # képkocka lépésenként
SCREENRECT = pygame.Rect(0, 0, szel*meret + diaSzel, mag*meret)  # a képkeret
bevitel_mutat = True
diagram_mutat = False
mezo_mutat = True

# Számolásokhoz

mezo = []  # a jelenlegi állapot
ujmezo = []  # a következő állapot
folyt = 0  # a megszakított számítás következő helye, ahol folytatni kell

roka_adatok = {"val": 0.05,
               "hal": 0.1,
               "szap": 0.6,
               "utod": 2,
               "megy": 2}
nyul_adatok = {"val": 0.4,
               "hal": 0.2,
               "szap": 0.8,
               "utod": 3,
               "megy": 1}
elnevezesek = {"val": "kezdeti állapotban a mezők elfoglalásának valószínűsége",
               "szap": "szaporodás valószínűsége (utódonként)",
               "utod": "utódok maximális száma",
               "hal": "halál valószínűsége",
               "megy": "táplálékkeresés maximális távolsága"}

########################################## OBJEKTUMOK ##############################################

# Róka

class Roka:
    def meghal(self):
        """halál megtörténtének megállapítása"""
        if random.random() < roka_adatok["hal"]:
            return True
        else:
            return False

    def eszik(self, x, y):
        """megevett nyúl megadása"""
        for i in range(roka_adatok["megy"]):
            return korbekeres(x, y, 'n', mezo, i+1, 1)

    def szaporodik(self):
        """utódok számának megadása"""
        eredm = 0
        for _ in range(roka_adatok["utod"]):
            if random.random() < roka_adatok["szap"]:
                eredm += 1
        return eredm


class Nyul:
    def meghal(self):
        """halál megtörténtének megállapítása"""
        if random.random() < nyul_adatok["hal"]:
            return True
        else:
            return False

    def eszik(self, x, y):
        """megevett fű megadása"""
        for i in range(nyul_adatok["megy"]):
            return korbekeres(x, y, 'f', mezo, i+1, 1)

    def szaporodik(self):
        """utódok számának megadása"""
        eredm = 0
        for i in range(nyul_adatok["utod"]):
            if random.random() < nyul_adatok["szap"]:
                eredm += 1
        return eredm


########################################## FÜGGVÉNYEK ##############################################

def korbekeres(x, y, mit, miben, r, db):
    """(x, y) körül az adott tömbben adott elemet keres (db mennyiségben),
    a legfeljebb r távolságban lévők közül véletlenszerűen választ."""
    if db==0:
        return []
    jok = []
    if y-r >= 0 and y-r < mag:
        for i in range(x-r, x+r):
            if i >= 0 and i < szel and miben[i][y-r] == mit:
                jok.append((i, y-r))
    if x-r >= 0 and x-r < szel:
        for i in range(y-r+1, y+r+1):
            if i >= 0 and i < mag and miben[x-r][i] == mit:
                jok.append((x-r, i))
    if y+r >= 0 and y+r < mag:
        for i in range(x-r+1, x+r+1):
            if i >= 0 and i < szel and miben[i][y+r] == mit:
                jok.append((i, y+r))
    if x+r >= 0 and x+r < szel:
        for i in range(y-r, y+r):
            if i >= 0 and i < mag and miben[x+r][i] == mit:
                jok.append((x+r, i))
    eredm = []
    db = min(len(jok), db)
    for _ in range(db):
        ssz = int(random.random()*len(jok))
        eredm.append(jok.pop(ssz))
    return eredm


def kitolt(mivel):
    """Az 'ujmezo' tömböt a megadott értékkel tölti ki."""
    global ujmezo
    ujmezo.clear()
    for _ in range(szel):
        ujmezo.append([mivel]*mag)


####################################################################################################
########################################## MODELLEZÉS ##############################################
####################################################################################################

def kezd():
    """beállítja a mező kezdeti állapotát"""
    for i in range(szel):
        mezo.append([None]*mag)
        ujmezo.append([])
        for _ in range(mag):
            val = random.random()
            if val < roka_adatok["val"]:
                ujmezo[i].append('rf')
            elif val < roka_adatok["val"] + nyul_adatok["val"]:
                ujmezo[i].append('nf')
            else:
                ujmezo[i].append('f')


############################################# LÉPÉS ################################################

def lep(arany=1):
    """egy lépés folyt-tól arany arányú részét elvégzi"""
    global mezo, ujmezo, folyt
    for i in range(folyt, int(len(mezo)*arany)):
        for j in range(len(mezo[i])):
            if mezo[i][j] == 'r':  # róka
                if not Roka.meghal(Roka):  # él
                    eredm = Roka.eszik(Roka, i, j)
                    if len(eredm) != 0:  # tud enni
                        x, y = eredm[0]
                        if mezo[x][y] != 'n':
                            raise RuntimeWarning("az utódot nem megfelelő helyre (" + mezo[x][y] + "-re) akarja tenni")
                        mezo[x][y] = 'f'
                        ujmezo[x][y] = 'rn' + str(i) + ' ' + str(j)
                        utod = Roka.szaporodik(Roka)  # szaporodik
                        eredm = korbekeres(x, y, 'f', ujmezo, 1, utod)
                        while len(eredm) > 0:
                            x, y = eredm.pop()
                            ujmezo[x][y] = 'r ' + str(i) + ' ' + str(j)
                    else:  # nem él
                        ujmezo[i][j] = 'fr'
                else:  # nem él
                    ujmezo[i][j] = 'fr'
            elif mezo[i][j] == 'n':  # nyúl
                if not Nyul.meghal(Nyul) and len(Nyul.eszik(Nyul, i, j)) > 0:  # él
                    ujmezo[i][j] = 'n ' + str(i) + ' ' + str(j)
                    utod = Nyul.szaporodik(Nyul)  # szaporodik
                    eredm = korbekeres(i, j, 'f', ujmezo, 1, utod)
                    while len(eredm) > 0:
                        x, y = eredm.pop()
                        ujmezo[x][y] = 'n ' + str(i) + ' ' + str(j)
                else:  # nem él
                    ujmezo[i][j] = 'fn'

    folyt = int(len(mezo)*arany)  # folytatás


####################################################################################################
############################################ KEZDÉS ################################################
####################################################################################################

def main():
    global mezo, ujmezo, folyt, bevitel_mutat, diagram_mutat
    szamlalo = 0  # a lejátszott képkockák számát adja meg
    kiir = [[None]*mag]*szel  # a kiírandó kockákat tartalmazza

    ####################################### KIÍRÓ FÜGGVÉNYEK ###########################################

    def kozt_poz(i, j):
        """megadja, hogy milyen köztes pozícióban található a kiir tömb adott eleme"""
        if len(kiir[i][j]) <= 1:
            return False
        elif len(kiir[i][j]) == 2:
            return True
        arany = (szamlalo%gyors) / gyors
        x, y = tuple(map(int, kiir[i][j][2:].split()))
        return x + (i-x)*arany, y + (j-y)*arany

    def atlatszosag(eloter, hatter, arany):
        """megadja egy áttetsző kocka színét"""
        return tuple([eloter[i] + (hatter[i]-eloter[i])*arany for i in range(3)])

    def nyil(irany, poz):
        """kirajzol egy adott irányba és pozícióba mutató nyílhegyet"""
        eltol = [j-i for i, j in zip(irany[1], poz)]
        a, b = tuple([tuple([j+k for j, k in zip(i, eltol)]) for i in irany])
        hossz = math.sqrt(sum([(i-j)**2 for i, j in zip(a, b)]))
        a = tuple([j + (i-j)/hossz*10 for i, j in zip(a, b)])
        pygame.draw.line(screen, (0, 0, 0), (a[0] + (b[1]-a[1])*4/10, a[1] + (b[0]-a[0])*4/10), b, 2)
        pygame.draw.line(screen, (0, 0, 0), (a[0] - (b[1]-a[1])*4/10, a[1] - (b[0]-a[0])*4/10), b, 2)

    ###################################### ALAP MEGALKOTÁSA ############################################

    pygame.init()
    screen = pygame.display.set_mode(SCREENRECT.size)  # a képernyő
    clock = pygame.time.Clock()  # az idő

    kezd()
    betu = pygame.font.SysFont("calibri", 16)  # betűstílus definiálása
    cim_betu = pygame.font.SysFont("calibri", 20, True)
    eger_poz = (0, 0)
    bev_mezo = None
    frissit = False
    beoszt = 50  # diagram beosztása
    populacio = {'r': [], 'n': []}  # populációk tárolása visszamenőleg

    ####################################################################################################
    ############################################ CIKLUS ################################################
    ####################################################################################################
    
    while True:
        events = pygame.event.get()

        # bezárás
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return

        ############################################ HÁTTÉR ################################################

        pygame.draw.rect(screen, (255, 255, 255), (szel*meret, 0, diaSzel, mag*meret))  # diagram (fehér)
        pygame.draw.rect(screen, szinek["f"], (0, 0, szel*meret, mag*meret))  # mező (zöld)

        ########################################### BEVITEL ################################################

        if bevitel_mutat:
            cim = cim_betu.render("Adatok megadása", True, (0, 0, 0), (255, 255, 255))
            cim_szel, _ = cim_betu.size("Adatok megadása")
            screen.blit(cim, (szel*meret+diaSzel/2-cim_szel/2, 10))
            betumagassag = 22

            #if bev_mezo is not None:
                #bev_mezo.update(events)

            #eger_poz = (0, 0)
            for es in events:
                if es.type == pygame.MOUSEBUTTONUP:
                    eger_poz = pygame.mouse.get_pos()
                    bev_mezo = None
                if es.type == pygame.KEYDOWN and es.key == pygame.K_RETURN:
                    frissit = True

            poz = (szel*meret+10, 40)
            kiirando = [(cim_betu.render("Nyúl:", True, (0, 0, 0), (255, 255, 255)), poz)]

            for valtozo in nyul_adatok:
                poz = (poz[0], poz[1]+betumagassag)
                kiirando.append((betu.render(elnevezesek[valtozo], True, (0, 0, 0), (255, 255, 255)), poz))
                poz = (poz[0], poz[1]+betumagassag)
                kiirando.append((betu.render(str(nyul_adatok[valtozo]), True, (0, 0, 0), (255, 255, 255)), poz))
                if pygame.Rect(poz+(diaSzel-10, 22)).collidepoint(eger_poz):
                    if bev_mezo is None:
                        bev_mezo = pygame_textinput.TextInput(str(nyul_adatok[valtozo]), "calibri", 16)
                    frissit = bev_mezo.update(events)
                    frissitett_adat = ("nyul", valtozo)
                    kiirando[-1] = (bev_mezo.get_surface(), poz)

            poz = (poz[0], poz[1]+betumagassag)
            kiirando.append((cim_betu.render("Róka:", True, (0, 0, 0), (255, 255, 255)), poz))
            for valtozo in roka_adatok:
                poz = (poz[0], poz[1]+betumagassag)
                kiirando.append((betu.render(elnevezesek[valtozo], True, (0, 0, 0), (255, 255, 255)), poz))
                poz = (poz[0], poz[1]+betumagassag)
                kiirando.append((betu.render(str(roka_adatok[valtozo]), True, (0, 0, 0), (255, 255, 255)), poz))
                if pygame.Rect(poz+(diaSzel-10, 22)).collidepoint(eger_poz):
                    if bev_mezo is None:
                        bev_mezo = pygame_textinput.TextInput(str(roka_adatok[valtozo]), "calibri", 16)
                    frissit = bev_mezo.update(events)
                    frissitett_adat = ("roka", valtozo)
                    kiirando[-1] = (bev_mezo.get_surface(), poz)

            #if bev_mezo is not None:
                #print(frissit, bev_mezo.get_text())
            if frissit and bev_mezo is not None:
                allat, valtozo = frissitett_adat
                tipus = type(globals()[allat + "_adatok"][valtozo])
                globals()[allat + "_adatok"][valtozo] = tipus(bev_mezo.get_text())
                print(roka_adatok, nyul_adatok)

            for ert in kiirando:
                szoveg, poz = ert
                screen.blit(szoveg, poz)

        ####################################### ÚJ LÉPÉS KEZDÉSE ###########################################

        if szamlalo % gyors == 0:
            kiir = copy.deepcopy(ujmezo)  # jelenlegi adatok kiírásra mentése
            db = {"r": 0, "n": 0}
            for i in range(len(ujmezo)):  # populációk meghatározása és mezo tömb frissítése
                for j in range(len(ujmezo[i])):
                    mezo[i][j] = ujmezo[i][j][0]
                    if mezo[i][j] == "n":
                        db["n"] += 1
                    elif mezo[i][j] == "r":
                        db["r"] += 1

            for allat in ['r', 'n']:
                populacio[allat].append(db[allat])

            # számolás előkészítése
            folyt = 0
            kitolt('f')

        ########################################### DIAGRAM ################################################

        if diagram_mutat:
            if len(populacio['n'])>1:  # értékek
                if len(populacio['n'])-1 + (szamlalo%gyors)/gyors > (diaSzel-60)/beoszt:
                    beoszt = (diaSzel-60)/(len(populacio['n']) + (szamlalo%gyors)/gyors -1)

                for allat in ['r', 'n']:
                    pontlista = list(zip([int(i*beoszt+szel*meret+30) for i in range(len(populacio[allat])-1)], map(lambda x: int(mag*meret-30-x/(szel*mag)*(mag*meret-60)), populacio[allat][:-1])))
                    pontlista.append([int((len(populacio[allat])-2+(szamlalo%gyors)/gyors)*beoszt+szel*meret+30), int(mag*meret-30-(populacio[allat][-2] + (populacio[allat][-1] - populacio[allat][-2])*(szamlalo%gyors)/gyors)/(szel*mag)*(mag*meret-60))])
                    pygame.draw.lines(screen, szinek[allat], False, pontlista, 3)

            # keret

            szoveg = betu.render("Populáció (db)", True, (0, 0, 0), (255, 255, 255))
            screen.blit(szoveg, (szel*meret + 3, 10))

            pygame.draw.line(screen, (0, 0, 0), (szel*meret + 30, 30), (szel*meret + 30, mag*meret - 10), 2)
            nyil(((szel*meret + 30, mag*meret - 10), (szel*meret + 30, 30)), (szel*meret + 30, 30))
            pygame.draw.line(screen, (0, 0, 0), (szel*meret + 10, mag*meret - 30), (szel*meret + diaSzel - 30, mag*meret - 30), 2)
            nyil(((szel*meret + 10, mag*meret - 30), (szel*meret + diaSzel - 30, mag*meret - 30)), (szel*meret + diaSzel - 30, mag*meret - 30))

        ############################################# MEZŐ #################################################

        if mezo_mutat:
            for i in range(len(kiir)):
                for j in range(len(kiir[i])):
                    poz = kozt_poz(i, j)
                    if type(poz) != bool:
                        if kiir[i][j][1] != ' ':
                            pygame.draw.rect(screen, szinek[kiir[i][j][1]], (i*meret, j*meret, meret, meret))
                        x, y = poz
                        pygame.draw.rect(screen, szinek[kiir[i][j][0]], (x*meret, y*meret, meret, meret))
                    elif poz is True:
                        pygame.draw.rect(screen, atlatszosag(szinek[kiir[i][j][1]], szinek[kiir[i][j][0]], (szamlalo % gyors) / gyors), (i*meret, j*meret, meret, meret))

        ########################################### OLDALSÁV ###############################################

        for es in events:
            if es.type == pygame.MOUSEBUTTONUP:
                if gomb.collidepoint(pygame.mouse.get_pos()):
                    bevitel_mutat = not bevitel_mutat
                    diagram_mutat = not diagram_mutat

        if bevitel_mutat:
            szo = "Diagram"
        elif diagram_mutat:
            szo = "Bevitel"

        szoveg = betu.render(szo, True, (0, 0, 0), (255, 255, 255))
        gomb_szel, gomb_mag = betu.size(szo)
        gomb = pygame.Rect((szel*meret+diaSzel-16-gomb_szel, mag*meret-11-gomb_mag, gomb_szel+10, gomb_mag+5))
        pygame.draw.rect(screen, (0, 0, 0), gomb, 2)
        screen.blit(szoveg, (szel*meret+diaSzel-11-gomb_szel, mag*meret-8-gomb_mag))

        ############################################# RAJZ #################################################

        pygame.display.update()

        lep((szamlalo%gyors+1)/gyors)
        clock.tick(10)
        szamlalo += 1


if __name__ == '__main__':
    main()
