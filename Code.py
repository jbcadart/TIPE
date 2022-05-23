from tkinter import *
import numpy as np
from math import *
import random
#1: Passage d'une carte net à une carte de pression

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from types import SimpleNamespace
import tkinter as tk
from tkinter import ttk

import json


class Vect2(tuple):
    def __add__(self, a):
        # TODO: check lengths are compatable.
        return Vect2(x + y for x, y in zip(self, a))
    def __sub__(self, a):
        # TODO: check lengths are compatable.
        return Vect2(x - y for x, y in zip(self, a))
    def __mul__(self, c):
        return Vect2(x * c for x in self)
    def __rmul__(self, c):
        return Vect2(c * x for x in self)
VectNul = Vect2( (0, 0) )



def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)





#================================================================

#ALERT !!
#Les coord de mes Cell sont TOUJOURS celles de son CENTRE (et pas celles de son coin bas gauche)
#ALERT !!

#On travaille en radians et en mètres
#le point de coordonées 0,0 se trouve en long = 0, lat = -latitudeMaxPoles
#la case d'indice 0, 0 se trouve en long = 0, lat = -latitudeMaxPoles


#constantes physiques
rayonTerre = 6.371e6
masse_vol_soufre = 32*10**-3    #je n'e ai actuellement aucune idée

#constantes relatives à la carte
#suseptibles d'être changées
largeurMondeCell  = 20 #nombre de Cells en largeur  (en Y)
longueurMondeCell = 50 #nombre de Cells en longueur (en X)

#on se place au level 80
#donc
a_lnsp =19620.042969
b_lnsp = 0.068448



latitudeMaxPoles = radians(45)                   #Au dessus de cet angle, on est dans les pôles
#donc
largeurMonde = 2*rayonTerre*sin(latitudeMaxPoles)                       #taille (en mètre) (et en Y) du monde
longueurMonde = 2*pi*rayonTerre                                         #taille (en mètre) (et en X) du monde
#donc
largeurCell = largeurMonde/largeurMondeCell   # (en mètre) la taille (en Y) d'une cell
longueurCell = longueurMonde/longueurMondeCell # (en mètre) de même
hauteurCell  = 10   # (en mètre) complétement arbitraire, ne sert que pour l'homogénéité des formules
#donc
A0 = largeurCell * longueurCell  #Aire d'une Cell
V0 = A0 * hauteurCell           #Volume d'une Cell

tkLongueurCell = 20 #(en pixel, uniquement pour le dessin)
tkLargeurCell = 20 #(en pixel, uniquement pour le dessin)


dt = 1

#constante calcul pression
constante=3.9*10**(-3)  #Constante  calculé dans la démo de la fonction passage_temperature_sol_pression(M,Tsol) dans l'open office
P0=100000
altitude=9000   #La température ne varie pas entre 9 et 20 km (à peu près)
g=9.81
R=8.31

def taille_case(carte_pression):
    """Prend la carte de pression et renvoie la taille réel des cases en m (hauteur de la case, largeur de la case)"""
    n,m=len(carte_pression),len(carte_pression[0])
    return largeurCell,longueurCell


#----------------------



Image = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Couleur_rogné.PNG" )
image_array = np.asarray( Image )    #asarray pour empecher la modification de l'image

# plt.imshow( image_array )
# plt.show()
#1 Passage température sur carte en couleur à matrice de température


passage_couleur_température=np.array( [[[73,61,217],[73,93,223],[85,74,219],-14 ], [[80,128,232],[93,163,241],[91,136,233],-10 ], [[105,193,248],[116,213,251],[113,191,247],-6 ], [[153,230,255],[179,238,249],[138,225,245],-2 ], [[51,242,150],[51,233,217],[97,240,177],2 ], [[51,211,109],[64,194,149],[45,171,125], 6], [[84,149,125],[51,142,84],[33,119,64], 10],  [[99,180,86],[148,217,89],[124,189,69],14 ], [[196,255,92],[224,249,180],[169,225,72],18 ],  [[255,248,51],[249,229,60],[225,218,33],22 ],  [[253,213,61],[253,189,55],[223,185,42],26 ], [[249,161,51],[255,133,51],[255,140,64],30 ], [[253,114,51],[255,52,255],[254,66,64],34 ],[[245,72,51],[245,70,129],[246,82,136],38 ], [[245,69,255],[221,63,163],[221,80,183],42 ], [[195,58,121],[170,53,77],[199,71,129],46 ]],dtype=object)

matrice_couleur=np.array([[[245,69,255,255],[99,180,86, 255],[195,58,121, 255]],[[253,213,61,255],[169,225,72,255] ,[255,248,51, 255] ]])
#Matrice 42,14,46// 26,18,22



def liste_pixels_possibles(i,j,carte):
    """Renvoie une liste de 16*3*2 éléments. Il s'agit des pixels possibles ou non de passage_couleur_température pouvant désigner la température de carte[i][j]. Ils sont accollés à un 0 ou un 1 selon que ce pixel soit possible ou non"""
    liste=[]
    for k in range(16):  #la liste passage_couleur_température contient 16 éléments
        for e in range(3):
            b=0      #0=True et 1= False
            for f in range(3):
                if abs(passage_couleur_température[k][e][f] - carte[i][j][f])>=60:   # Lien entre les pixels et les couleurs
                    b=1
            liste.append(b)   #Au final, elle est de de taille 16*3*2. Les 0 donnent les triplets cohérent en température
            liste.append(e)
    return liste



température=np.zeros(6)
température=température.reshape(2,3)



def liste_pixels_possibles_2(i,j,carte,matrice_température):
    """Idem mais en vérifiant une certaine continuité entre la case et la case précédente sur la ligne"""
    liste=[]
    for k in range(16):  #la liste passage_couleur_température contient 16 éléments
        for e in range(3):
            b=0
            for f in range(3):
                if abs(passage_couleur_température[k][e][f] - carte[i][j][f])>=60:   # Lien entre les pixels et les couleurs
                    b=1
            if abs(matrice_température[i][j-1] - passage_couleur_température[k][3])>=16: #Condition de continuité de la température
                b=1
            liste.append(b)   #Finalement, elle est de de taille 16. Les True donnent les lieux cohérent en température
            liste.append(e)
    return liste


#liste_pixels_possibles_2(1,2,matrice_couleur,température)
#[1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2]


def indice_RGB(carte,liste,i,j,e,n):
    """Donne l'indice dans la liste correspondant à la température associé au pixel étudié"""
    indice=0
    for k in range(16):
        valeur=1000     #Ecart entre le pixel étudié est celui de référence
        if liste[6*k]==0 or liste[6*k+2]==0 or liste[6*k+4]==0:
            rep=True    #La température associée à ces 3 éléments est possible
            if liste[k*6]==0:
                e=liste[6*k+1]    #e est le triplet RGB possiblement caractéristique du pixel étudié
                valeur1=0
                for f in range(3):
                    valeur1+=abs(passage_couleur_température[k][e][f] - carte[i][j][f])
                valeur=min(valeur,valeur1)
            elif liste[6*k+2]==0 :
                e=liste[6*k+2]
                valeur2=0
                for f in range(3):
                    valeur2+=abs(passage_couleur_température[k][e][f] - carte[i][j][f])
                valeur=min(valeur,valeur2)    #On conserve la difference la plus faible
            elif liste[6*k+4]==0:
                e=liste[6*k+5]
                valeur3=0
                for f in range(3):
                    valeur3+=abs(passage_couleur_température[k][e][f] - carte[i][j][f])
                valeur=min(valeur,valeur3)
        else:
            valeur=1000      #Cas d'une température non caractéristique du pixel
        if valeur<n:
            n=valeur
            indice=k
    return indice




def verification_1(liste):
    for i in range(len(liste)//2):
        if liste[2*i]==0:
            return False
    return True




def passage_carte_couleur_carte_température(carte):
    n,m=len(carte),len(carte[0])
    mat_temp=np.zeros(n*m)
    mat_temp=mat_temp.reshape(n,m)
    for i in range(n):
        liste_couleur=liste_pixels_possibles(i,0,carte)
        indice=indice_RGB(carte,liste_couleur,i,0,e,1000)    #indice de la liste numpy associé à la température à renvoyer. 1000 car les différences entre les pixels étudiés et les pixels de références sont bien inférieur à 1000
        mat_temp[i][0]=passage_couleur_température[indice][3]
        if i!=0:
            if abs(mat_temp[i-1][0]- mat_temp[i][0])>=12:
                mat_temp[i][0]=mat_temp[i-1][0]

        for j in range(1,m):            #On traite le cas général
            liste_couleur=liste_pixels_possibles_2(i,j,carte,mat_temp)

            if verification_1(liste_couleur):
                mat_temp[i][j]=mat_temp[i][j-1]    #On s'assure de la continuité avec la cae précédente si le pixel est illisible
            else:
                rep=False
                indice=indice_RGB(carte,liste_couleur,i,j,e,1000)
                if rep:
                    mat_temp[i][j]=mat_temp[i][j-1]
                else:
                    mat_temp[i][j]=passage_couleur_température[indice][3]  #On extraie la température associée  à l'indice pour lequel cette différence est la plus faible
            if i!=0:
                if abs(mat_temp[i-1][j]- mat_temp[i][j])>=12:
                    mat_temp[i][j]=mat_temp[i-1][j]
    return mat_temp



#matrice_temp_couleur=passage_carte_couleur_carte_température(matrice_couleur)

#verification: la commande passage_carte_couleur_carte_température(matrice_couleur) renvoie:
#array([[42., 42., 46.],
 #      [26., 18., 22.]])


#matrice=passage_carte_couleur_carte_température(image_array)

# with open('output.txt','w') as f1:
#     json.dump(matrice.tolist(),f1)

#matrice[120]
'''array([10., 10., 10., 10.,  6., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 14., 14.,
       14., 14., 14., 14., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 14., 14., 14., 10., 10., 14., 18., 14., 14., 14., 18., 14.,
       14., 18., 18., 18., 18., 18., 18., 14., 10., 10., 10., 10., 10.,
       10., 14., 14., 14., 14., 14., 14., 10., 10., 10., 14., 18., 22.,
       26., 26., 18., 18., 18., 18., 18., 18., 18., 18., 18., 18., 18.,
       18., 22., 22., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 22., 22.,
       26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       18., 10., 10., 14., 18., 22., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 26., 18., 18., 18., 18., 18., 18., 18., 18., 18., 18.,
       14., 14., 14., 14., 10., 10., 10., 10., 10., 14., 14., 14., 10.,
       10., 14., 10., 14., 14., 18., 18., 18., 14., 14., 10., 10., 10.,
       10., 10., 14., 18., 18., 18., 14., 14., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
        6., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10.,  6.,  6.,  6., 10., 14., 14., 14., 14.,
       10., 10., 10., 14., 14., 10., 10., 10., 14., 14., 18., 18., 14.,
       14., 14., 14., 14., 14., 18., 18., 18., 18., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 18., 18., 18., 18., 18., 18.,
       18., 18., 18., 18., 18., 18., 18., 18., 22., 26., 30., 30., 30.,
       30., 30., 30., 30., 30., 26., 26., 26., 26., 26., 30., 30., 26.,
       26., 26., 18., 14., 18., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 22., 22., 22., 22., 22., 22., 14., 18., 22., 22., 22., 22.,
       26., 22., 26., 26., 26., 26., 22., 22., 22., 22., 18., 18., 18.,
       18., 18., 18., 18., 18., 14., 14., 18., 18., 18., 18., 18., 18.,
       18., 18., 18., 14., 14., 14., 14., 14., 14., 14., 14., 14., 14.,
       14., 14., 14., 14., 14., 14., 14., 14., 14., 10., 10., 10., 14.,
       14., 14., 18., 18., 18., 22., 26., 26., 26., 26., 26., 26., 26.,
       18., 18., 18., 18., 18., 18., 18., 14., 14., 14., 14., 22., 26.,
       30., 30., 30., 26., 26., 26., 30., 30., 30., 30., 30., 30., 30.,
       30., 30., 30., 30., 22., 26., 26., 26., 30., 30., 30., 30., 30.,
       30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 26.,
       26., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30., 30.,
       26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 18.,
       18., 18., 18., 18., 14., 14., 18., 18., 18., 18., 18., 26., 18.,
       18., 26., 30., 30., 30., 34., 34., 34., 34., 34., 34., 34., 30.,
       30., 34., 34., 34., 30., 30., 30., 26., 26., 26., 26., 30., 30.,
       34., 34., 34., 30., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 22., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       30., 30., 30., 26., 30., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 26., 26., 26., 26., 22., 22., 22., 22., 22., 26., 26.,
       26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26., 26.,
       26., 26., 26., 26., 26., 26., 18., 18., 18., 18., 18., 22., 22.,
       22., 22., 26., 22., 26., 26., 26., 26., 26., 22., 22., 22., 18.,
       18., 14., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 18., 18., 18., 18., 10., 14., 10., 10., 10., 10.,
       10., 10.,  6.,  6.,  6., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,
        6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,
        6., 10., 10., 10.,  6.,  6.,  6.,  6., 10., 10., 10., 10., 10.,
        6.,  6.,  6.,  6.,  6., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10., 10.,
       10., 10., 10., 10., 10., 10., 10., 10., 10., 10.]
'''




#2 Passage carte de température à carte de température moyennée

"""On écrit d'abord des constantes"""




#Travail Théo

class Cell:

    def __init__(self, estUnPole, masse, i, j, taille = Vect2((longueurCell, largeurCell))):

        if estUnPole:
            self.m = masse                                          #masse de SOUFRE dans la Cell

            self.a = Vect2((0, 0))                                  #acc de l'AIR
            self.v = Vect2((0, 0))                                  #vitesse de l'AIR

            self.t = taille                                         #Taille (largeur longueur) de la cell
            self.V = self.t[0]*self.t[1]*hauteurCell                #volume de la cell

            self.ij = (i, j)
            self.coord = Vect2(((i+0.5)*longueurCell, (j+0.5)*largeurCell))

            self.pression = 0                                       #valeur par défaut

            #==========================
            #variables seulement pour l'importation de la base de données
            self.val = 0
            self.nbData = 0

        else:
            self.m = masse                                          #masse de SOUFRE dans la Cell
            self.a = Vect2((0, 0))                                  #acc de l'AIR
            self.v = Vect2((0, 0))                                  #vitesse de l'AIR

            self.t = taille                                         #Taille (largeur longueur) de la cell
            self.V = self.t[0]*self.t[1]*hauteurCell                #volume de la cell

            self.ij = (i, j)
            self.coord = Vect2(((i+0.5)*longueurCell, (j+0.5)*largeurCell))

            self.pression = 0                                       #valeur par défaut

            #==========================
            #variables seulement pour l'importation de la base de données
            self.val = 0
            self.nbData = 0


class Carte: #l'objet que doit gérer Jb

   
#3: Passage d'une situation initiale (quantité de matière initiale, sa position, la vitesse initiale en tout point) à une table de l'instant initiale


    def __init__(self): #Par exemple

        self.cells = []

        for i in range(longueurMondeCell):
            self.cells.append([])
            for j in range(largeurMondeCell):
                self.cells[i].append(Cell(False, 0, i, j, Vect2((longueurCell, largeurCell)))) #on initialise les cell à une qté nulle de soufre
                #self.cells[i][j] =

        self.poleNord = Cell(True, 0, -1, -1)
        self.poleSud = Cell(True, 0, -1, -1)

    def cellFromCoord(self, coord):
        #Je mets en entrée des distances (en Mètres)

        x = coord[0]
        y = coord[1]

        if abs(y) > largeurMonde:
            if y < 0:
                return self.poleSud
            else:
                return self.poleNord
        else:
            indX = int(x//longueurCell)
            indY = int(y//largeurCell)

            return self.cells[indX][indY]

    def cellFromLatLongRad(self, latitude, longitude):
        #je mets en entrée des coordonnées du monde réel ***(latitude longitude)***. L'entrée peut être négative, pointer sur les pôles, être à la jonction de 2 cells
        #j'ai en sortie la cell dans laquelle je tombe (donc soit une cell, soit les pôles)
        #si je suis sur une ligne, c'est le droite haut qui gagne

        #Mes lat,long sont des RADIANS, et sont algébriques

        if abs(latitude) >= latitudeMaxPoles:
            if latitude > 0:
                return self.poleNord
            else:
                return self.poleSud

        else:
            largeurCalc = rayonTerre*sin(latitude)  #on a une distance
            indY = int((largeurCalc + largeurMonde/2)//largeurCell)

            longueurCalc = longitude*rayonTerre      #on a une distance
            indX = int(longueurCalc//longueurCell)

            return self.cells[indX][indY]

    def cellFromLatLongDeg(self, latitude, longitude):
        return self.cellFromLatLongRad(radians(latitude), radians(longitude))


    def cellsFromCellAndCoord(self, cell):
        #c'est le fameux truc que j'ai demandé à Cointault : quand j'additione les coords de la case à son vecteur vitesse, quelles cases je touche et dans quelles proportions ?
        #en sortie j'ai une liste tuples (cell, float) avec les cells que je touche et quelle proportion (avec le float)

        coord = cell.coord

        #je sais quelles cases mes extrémités touchent
        coordCoinDH = coord + Vect2( ( cell.t[0]/2,  cell.t[1]/2) ) + cell.v #coin droite haut
        coordCoinDB = coord + Vect2( ( cell.t[0]/2, -cell.t[1]/2) ) + cell.v
        coordCoinGB = coord + Vect2( (-cell.t[0]/2, -cell.t[1]/2) ) + cell.v
        coordCoinGH = coord + Vect2( (-cell.t[0]/2,  cell.t[1]/2) ) + cell.v

        cellCoinDH = self.cellFromCoord(coordCoinDH)
        cellCoinDB = self.cellFromCoord(coordCoinDB)
        cellCoinGB = self.cellFromCoord(coordCoinGB)
        cellCoinGH = self.cellFromCoord(coordCoinGH)

        xinter = (coordCoinDH[0] // longueurCell) #+ coordCoinDH[0] % longueurCell
        yinter = (coordCoinDH[1] // largeurCell) #+ coordCoinDH[1] % largeurCell
        vectInter = Vect2((xinter, yinter))

        aireDH = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        aireDB = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        aireGB = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        aireGH = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        #normalement, on a aireDH + ... + aireGH = largeurCell*longueurCell (=A0)

        rep = []
        rep.append( (cellCoinDH, aireDH/A0) )
        rep.append( (cellCoinDB, aireDB/A0) )
        rep.append( (cellCoinGB, aireGB/A0) )
        rep.append( (cellCoinGH, aireGH/A0) )

        #donc return [ [cell, float]; [...] ]
        return rep

    #4 Passage de la carte des vitesses de l'instant t à l'instant t+dt
    def accToVitesse(self, cell):
        cell.v += cell.a * dt

    def updateCells(self, matriceAccAir):

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):

                cell = self.cells[i][j]

                cell.a = Vect2((0, 0))
                cell.a = matriceAccAir[i][j]

                self.accToVitesse(cell)


                destinations = self.cellsFromCellAndCoord(cell)
                #on enlève le soufre dans la case originelle
                m0 = cell.m
                cell.m = 0
                #pour enventuellement le remettre si il ne s'est pas trop déplacé
                for e in destinations:
                    if e.estUnPole:
                        #à remplir
                        a = 1
                    else:
                        e[0].val += m0*e[1]    #on le met dans .val temporairement car on ne peut pas le mettre directement dans .m


        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                cell = self.cells[i][j]

                cell.m = cell.val

    def passageTempPression(self):
        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                c0 = self.cells[i][j]
                c0.pression = P0*((c0.val + 273.15-constante*altitude)/(c0.val+273.15))**(masse_vol_soufre*g/(constante*R))


# def passage_température_sol_pression(M,Tsol):  #M en kg/mol, Tsol la température au sol
#     return P0*((Tsol-constante*altitude)/Tsol)**(M*g/(constante*R)) #Demo dans l'open office
#
# #passage_temperature_sol_pression(32*10**-3,300)
# # 29961.576428490323
#
#
#
# def passage_carte_température_pression(M,matrice_température):  #M en kg/mol car g en m3/(kg.s)
#     n,m=len(matrice_température),len(matrice_température[0])
#     matrice_pression=np.zeros(n*m)
#     matrice_pression=matrice_pression.reshape(n,m)
#     for i in range(n):
#         for j in range(m):
#             matrice_pression[i][j]=passage_température_sol_pression(M,matrice_température[i][j])
#     return matrice_pression


    def draw(self):

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                canvas.create_rectangle( i*tkLongueurCell, j*tkLargeurCell,
                                         (i+1)*tkLongueurCell, (j+1)*tkLargeurCell,
                                         fill="red", dash=(1))



#Passage température globale à température moyennée

#Passage température pression




def importBigArray(carte0, ba):
    #[temp]

    n = len(ba)
    m = len(ba[0])

    #on calcule la taille (en "mètres") d'un pixel
    longueurPixelX = longueurMonde/m
    largeurPixelY = largeurMonde/n

    for i in range(n):
        for j in range(m):
            #!!!!!! Le point 0, 0 est en haut à gauche alors que moi il est en bas à gauche
            cell0 = carte0.cellFromCoord(Vect2( ( (j)*longueurPixelX, (n-i)*largeurPixelY) ))
            cell0.val += ba[i][j]
            cell0.nbData += 1

    for i in range(longueurMondeCell):
        for j in range(largeurMondeCell):
            if (carte0.cells[i][j].nbData != 0):
                carte0.cells[i][j].val = carte0.cells[i][j].val/carte0.cells[i][j].nbData

    carte0.passageTempPression()
    #Calcul pression finale
    #on se place au "level" 80

#     for i in range(longueurMondeCell):
#         for j in range(largeurMondeCell):
#             carte0[i][j].pression = carte0[i][j].val*a_lnsp + b_lnsp

carte_init=Carte()
importBigArray(carte_init,matrice)


for i in range(longueurMondeCell):
    ls = []
    for j in range(largeurMondeCell):
        ls.append(carte_init.cells[i][j].val)
    #print(ls)





"""[9.43859649122807, 10.19047619047619, 14.1203007518797, 16.776942355889723, 22.370927318295738, 24.68671679197995, 26.42105263157895, 26.42105263157895, 26.42105263157895, 26.42105263157895, 26.42105263157895, 25.318295739348372, 17.17794486215539, 11.416267942583731, 9.80952380952381, 6.822055137844612, 6.802005012531328, 5.819548872180451, 5.2180451127819545, 6.382775119617225]
[9.037037037037036, 10.56084656084656, 14.613756613756614, 18.0, 22.84656084656085, 27.703703703703702, 30.0, 30.0, 30.0, 30.0, 30.0, 28.423280423280424, 18.486772486772487, 12.070707070707071, 9.417989417989418, 6.634920634920635, 6.0, 5.439153439153439, 5.735449735449736, 6.161616161616162]
[7.841269841269841, 9.661375661375661, 12.16931216931217, 17.07936507936508, 21.61904761904762, 28.04232804232804, 30.0, 30.0, 30.0, 30.0, 30.0, 28.56084656084656, 21.682539682539684, 14.656565656565656, 9.947089947089948, 9.047619047619047, 7.439153439153439, 12.116402116402117, 10.677248677248677, 6.313131313131313]
[7.037037037037037, 9.904761904761905, 10.920634920634921, 16.444444444444443, 22.59259259259259, 28.137566137566136, 30.0, 30.0, 30.0, 30.0, 29.95767195767196, 28.253968253968253, 24.793650793650794, 15.878787878787879, 10.55026455026455, 9.947089947089948, 10.285714285714286, 14.010582010582011, 15.915343915343914, 8.94949494949495]
[6.01058201058201, 7.375661375661376, 12.243386243386244, 16.444444444444443, 23.67195767195767, 28.84656084656085, 30.0, 30.0, 30.0, 30.0, 29.227513227513228, 26.074074074074073, 24.814814814814813, 16.454545454545453, 10.814814814814815, 10.0, 9.97883597883598, 9.798941798941799, 12.158730158730158, 9.797979797979798]
[6.0, 8.338624338624339, 11.11111111111111, 16.19047619047619, 24.719576719576718, 29.61904761904762, 30.0, 30.0, 30.0, 30.0, 27.523809523809526, 24.941798941798943, 19.77777777777778, 15.535353535353535, 9.25925925925926, 8.666666666666666, 8.666666666666666, 5.693121693121693, 8.433862433862434, 8.181818181818182]
[6.0, 7.238095238095238, 10.518518518518519, 16.052910052910054, 25.608465608465607, 29.77777777777778, 30.0, 30.0, 30.0, 30.0, 26.793650793650794, 19.227513227513228, 18.0, 14.727272727272727, 9.735449735449736, 9.936507936507937, 10.455026455026456, 8.455026455026456, 5.470899470899471, 4.03030303030303]
[6.0, 7.00250626566416, 10.421052631578947, 16.235588972431078, 25.57894736842105, 28.887218045112782, 30.0, 30.0, 30.0, 30.0, 25.67919799498747, 18.0, 16.576441102756892, 14.392344497607656, 10.070175438596491, 8.265664160401002, 8.015037593984962, 9.137844611528822, 7.283208020050125, 9.674641148325358]
[6.0, 6.9523809523809526, 10.412698412698413, 16.063492063492063, 24.793650793650794, 26.761904761904763, 29.01010101010101, 30.0, 30.0, 30.0, 26.243386243386244, 17.83068783068783, 20.021164021164022, 26.767676767676768, 14.55026455026455, 6.264550264550264, 9.619047619047619, 12.402116402116402, 13.513227513227513, 9.535353535353535]
[6.0, 7.915343915343915, 10.634920634920634, 16.021164021164022, 21.174603174603174, 26.0, 26.19191919191919, 29.841269841269842, 30.0, 30.0, 28.243386243386244, 23.767195767195766, 31.77777777777778, 26.434343434343436, 14.465608465608465, 13.470899470899472, 11.767195767195767, 9.83068783068783, 6.021164021164021, 6.01010101010101]
[6.7936507936507935, 9.936507936507937, 10.613756613756614, 15.291005291005291, 19.005291005291006, 26.0, 26.0, 29.746031746031747, 29.85185185185185, 30.0, 30.253968253968253, 32.264550264550266, 35.714285714285715, 26.91919191919192, 19.67195767195767, 14.296296296296296, 12.433862433862434, 5.724867724867725, 0.8783068783068783, 3.505050505050505]
[14.126984126984127, 15.333333333333334, 15.661375661375661, 18.55026455026455, 22.158730158730158, 27.555555555555557, 27.555555555555557, 30.613756613756614, 30.17989417989418, 31.11111111111111, 32.148148148148145, 34.2010582010582, 37.31216931216931, 33.76767676767677, 22.634920634920636, 12.243386243386244, 7.798941798941799, 2.582010582010582, 0.2751322751322751, -1.9292929292929293]
[26.825396825396826, 27.333333333333332, 27.48148148148148, 29.037037037037038, 30.391534391534393, 32.4973544973545, 32.666666666666664, 33.96825396825397, 33.07936507936508, 33.41798941798942, 34.13756613756614, 28.804232804232804, 31.343915343915345, 27.646464646464647, 19.037037037037038, 12.804232804232804, 3.7248677248677247, 2.8994708994708995, 0.6878306878306878, -2.9494949494949494]
[9.925925925925926, 9.841269841269842, 11.671957671957673, 16.105820105820104, 18.0, 19.185185185185187, 22.535353535353536, 23.164021164021165, 24.296296296296298, 24.73015873015873, 24.962962962962962, 25.428571428571427, 26.687830687830687, 22.515151515151516, 15.43915343915344, 14.052910052910052, 2.1587301587301586, 1.3968253968253967, 1.8518518518518519, -0.42424242424242425]
[9.839598997493734, 9.157894736842104, 11.43358395989975, 14.160401002506266, 16.7468671679198, 17.88972431077694, 17.57894736842105, 21.839598997493734, 22.862155388471177, 28.285714285714285, 30.07017543859649, 29.92982456140351, 29.789473684210527, 23.645933014354068, 15.353383458646617, 12.897243107769423, 6.260651629072682, 3.5538847117794488, 3.3834586466165413, 1.9330143540669857]
[19.62962962962963, 19.26984126984127, 20.465608465608465, 21.767195767195766, 20.719576719576718, 20.941798941798943, 23.32323232323232, 28.32804232804233, 27.566137566137566, 30.433862433862434, 30.91005291005291, 30.0, 26.73015873015873, 20.02020202020202, 14.37037037037037, 11.26984126984127, 4.190476190476191, 3.9894179894179893, 1.1746031746031746, -1.2323232323232323]
[7.767195767195767, 9.915343915343914, 10.56084656084656, 14.444444444444445, 17.77777777777778, 19.608465608465607, 24.1010101010101, 26.52910052910053, 26.04232804232804, 29.83068783068783, 30.0, 30.0, 26.201058201058203, 20.80808080808081, 9.788359788359788, 7.925925925925926, 3.7248677248677247, 2.0423280423280423, -2.3174603174603177, -5.383838383838384]
[6.126984126984127, 7.608465608465608, 9.915343915343914, 12.402116402116402, 16.211640211640212, 17.227513227513228, 22.303030303030305, 27.25925925925926, 26.571428571428573, 29.80952380952381, 30.0, 29.693121693121693, 26.063492063492063, 22.535353535353536, 9.46031746031746, 6.751322751322752, 5.492063492063492, 6.0, 3.6507936507936507, 0.8484848484848485]
[6.0, 6.497354497354498, 9.97883597883598, 13.788359788359788, 17.48148148148148, 18.857142857142858, 21.272727272727273, 28.78306878306878, 28.941798941798943, 30.0, 30.0, 28.021164021164022, 26.0, 18.272727272727273, 9.248677248677248, 7.703703703703703, 6.0, 4.349206349206349, -5.238095238095238, -5.757575757575758]
[5.925925925925926, 6.0, 9.206349206349206, 13.058201058201059, 17.67195767195767, 24.984126984126984, 27.22222222222222, 30.32804232804233, 30.03174603174603, 30.0, 30.0, 28.105820105820104, 26.0, 18.646464646464647, 14.39153439153439, 9.121693121693122, 6.751322751322752, 5.98941798941799, 3.164021164021164, -8.16161616161616]
[5.925925925925926, 6.0, 8.804232804232804, 15.576719576719576, 21.195767195767196, 28.211640211640212, 30.0, 30.497354497354497, 30.0, 30.0, 27.44973544973545, 26.88888888888889, 23.650793650793652, 17.393939393939394, 14.126984126984127, 9.968253968253968, 10.0, 9.142857142857142, 6.857142857142857, 0.8181818181818182]
[5.839598997493734, 7.152882205513785, 10.882205513784461, 16.857142857142858, 25.05764411027569, 29.36842105263158, 30.0, 30.0, 30.0, 30.0, 26.852130325814535, 26.0, 23.614035087719298, 16.976076555023923, 14.0, 10.481203007518797, 9.679197994987469, 9.849624060150376, 9.328320802005013, 4.440191387559809]
[6.0, 7.619047619047619, 11.164021164021165, 17.185185185185187, 24.349206349206348, 26.677248677248677, 27.595959595959595, 27.354497354497354, 27.49206349206349, 27.904761904761905, 25.915343915343914, 25.058201058201057, 21.80952380952381, 17.8989898989899, 14.116402116402117, 13.132275132275133, 10.126984126984127, 9.587301587301587, 8.16931216931217, 6.090909090909091]
[10.624338624338625, 11.714285714285714, 14.920634920634921, 19.417989417989418, 25.502645502645503, 26.22222222222222, 27.484848484848484, 28.55026455026455, 28.137566137566136, 30.14814814814815, 35.682539682539684, 31.132275132275133, 24.296296296296298, 19.525252525252526, 14.328042328042327, 14.126984126984127, 12.296296296296296, 9.671957671957673, 8.476190476190476, 6.0]
[18.095238095238095, 18.38095238095238, 20.095238095238095, 22.624338624338623, 24.804232804232804, 28.17989417989418, 29.616161616161616, 32.22222222222222, 32.232804232804234, 37.17460317460318, 44.0, 45.767195767195766, 37.523809523809526, 30.1010101010101, 19.43915343915344, 15.153439153439153, 13.862433862433862, 10.105820105820106, 9.121693121693122, 7.222222222222222]
[5.005291005291006, 6.476190476190476, 9.724867724867725, 12.793650793650794, 16.285714285714285, 20.137566137566136, 25.363636363636363, 28.59259259259259, 28.761904761904763, 33.56613756613756, 39.925925925925924, 38.15873015873016, 35.94708994708995, 26.565656565656564, 27.047619047619047, 20.93121693121693, 11.947089947089948, 10.074074074074074, 9.947089947089948, 9.797979797979798]
[5.2592592592592595, 6.021164021164021, 9.693121693121693, 11.798941798941799, 15.386243386243386, 17.682539682539684, 23.424242424242426, 28.59259259259259, 26.994708994708994, 31.44973544973545, 36.48677248677249, 35.78835978835979, 30.211640211640212, 25.525252525252526, 22.8994708994709, 24.41269841269841, 17.280423280423282, 14.476190476190476, 12.529100529100528, 9.585858585858587]
[5.2063492063492065, 6.0, 9.428571428571429, 13.597883597883598, 15.65079365079365, 22.814814814814813, 27.03030303030303, 30.455026455026456, 28.814814814814813, 34.074074074074076, 38.63492063492063, 33.58730158730159, 24.476190476190474, 21.90909090909091, 23.555555555555557, 21.25925925925926, 16.51851851851852, 14.687830687830688, 11.492063492063492, 7.262626262626263]
[5.949874686716792, 6.491228070175438, 10.962406015037594, 18.401002506265666, 19.774436090225564, 22.69172932330827, 24.870813397129186, 29.588972431077693, 31.724310776942357, 35.9749373433584, 35.152882205513784, 32.526315789473685, 26.80200501253133, 18.3444976076555, 18.902255639097746, 21.278195488721803, 17.98997493734336, 13.478696741854636, 8.997493734335839, 6.526315789473684]
[13.343915343915343, 14.380952380952381, 17.15343915343915, 24.285714285714285, 28.04232804232804, 27.746031746031747, 28.848484848484848, 29.142857142857142, 31.015873015873016, 40.35978835978836, 43.65079365079365, 36.86772486772487, 28.063492063492063, 15.222222222222221, 16.402116402116402, 17.80952380952381, 15.989417989417989, 8.677248677248677, 6.338624338624339, 4.5353535353535355]
[16.126984126984127, 17.026455026455025, 19.238095238095237, 25.047619047619047, 29.206349206349206, 31.873015873015873, 31.77777777777778, 32.2962962962963, 32.68783068783069, 30.59259259259259, 35.64021164021164, 36.613756613756614, 33.24867724867725, 20.616161616161616, 15.216931216931217, 17.375661375661377, 12.306878306878307, 6.423280423280423, 5.343915343915344, 4.929292929292929]
[24.0, 24.70899470899471, 26.285714285714285, 30.296296296296298, 33.93650793650794, 35.48148148148148, 36.515151515151516, 36.666666666666664, 36.3068783068783, 34.4973544973545, 35.26984126984127, 36.666666666666664, 30.835978835978835, 20.151515151515152, 21.21693121693122, 16.74074074074074, 10.253968253968255, 4.698412698412699, 4.1798941798941796, 5.212121212121212]
[36.0, 36.0, 36.0, 36.17989417989418, 34.08465608465608, 32.592592592592595, 34.0, 34.0, 34.0, 34.476190476190474, 40.03174603174603, 42.402116402116405, 32.67724867724868, 25.707070707070706, 25.005291005291006, 16.497354497354497, 9.62962962962963, 5.365079365079365, 4.8465608465608465, 3.484848484848485]
[32.22222222222222, 32.22222222222222, 32.783068783068785, 33.925925925925924, 33.97883597883598, 35.06878306878307, 36.22222222222222, 36.22222222222222, 36.22222222222222, 36.22222222222222, 36.888888888888886, 39.32275132275132, 36.08465608465608, 31.232323232323232, 27.597883597883598, 19.015873015873016, 14.211640211640212, 10.835978835978835, 6.148148148148148, 4.282828282828283]
[27.333333333333332, 27.77777777777778, 29.026455026455025, 30.814814814814813, 31.44973544973545, 32.02116402116402, 33.01010101010101, 33.026455026455025, 33.111111111111114, 33.111111111111114, 33.386243386243386, 35.47089947089947, 28.761904761904763, 25.636363636363637, 27.227513227513228, 19.21693121693122, 17.312169312169313, 17.64021164021164, 12.878306878306878, 4.828282828282828]
[9.979949874686717, 13.157894736842104, 16.95739348370927, 19.273182957393484, 21.588972431077693, 24.99749373433584, 26.61244019138756, 26.69172932330827, 26.842105263157894, 26.06015037593985, 27.152882205513784, 32.51629072681704, 23.092731829573935, 15.483253588516746, 24.526315789473685, 23.343358395989974, 19.63408521303258, 19.473684210526315, 16.967418546365916, 5.559808612440191]
[7.132275132275132, 11.851851851851851, 15.386243386243386, 18.73015873015873, 22.296296296296298, 26.0, 25.505050505050505, 24.433862433862434, 24.22222222222222, 24.433862433862434, 24.634920634920636, 24.91005291005291, 17.95767195767196, 25.08080808080808, 24.444444444444443, 26.03174603174603, 25.005291005291006, 19.174603174603174, 16.137566137566136, 5.474747474747475]
[18.22222222222222, 19.07936507936508, 20.825396825396826, 22.645502645502646, 24.455026455026456, 27.24867724867725, 29.333333333333332, 29.555555555555557, 29.555555555555557, 29.555555555555557, 29.798941798941797, 26.92063492063492, 12.529100529100528, 21.353535353535353, 23.185185185185187, 22.941798941798943, 27.978835978835978, 21.058201058201057, 15.492063492063492, 4.151515151515151]
[6.0, 6.7407407407407405, 10.19047619047619, 14.804232804232804, 19.62962962962963, 24.73015873015873, 27.484848484848484, 27.77777777777778, 28.296296296296298, 28.201058201058203, 27.96825396825397, 24.444444444444443, 7.841269841269841, 22.87878787878788, 21.80952380952381, 20.03174603174603, 25.174603174603174, 19.238095238095237, 15.216931216931217, 6.242424242424242]
[6.0, 7.873015873015873, 10.433862433862434, 15.43915343915344, 18.38095238095238, 25.862433862433864, 29.7979797979798, 30.063492063492063, 30.50793650793651, 29.883597883597883, 28.88888888888889, 22.6984126984127, 18.052910052910054, 26.161616161616163, 25.07936507936508, 23.724867724867725, 22.074074074074073, 17.333333333333332, 13.174603174603174, 6.383838383838384]
[15.555555555555555, 16.582010582010582, 18.719576719576718, 22.105820105820104, 23.925925925925927, 28.465608465608465, 31.11111111111111, 31.46031746031746, 33.22751322751323, 29.947089947089946, 29.841269841269842, 25.227513227513228, 21.417989417989418, 26.0, 26.14814814814815, 23.96825396825397, 16.253968253968253, 16.211640211640212, 10.656084656084657, 11.070707070707071]
[6.074074074074074, 9.047619047619047, 11.28042328042328, 15.989417989417989, 20.52910052910053, 25.756613756613756, 29.171717171717173, 28.973544973544975, 28.867724867724867, 29.11111111111111, 28.835978835978835, 26.211640211640212, 22.391534391534393, 25.232323232323232, 24.56084656084656, 24.16931216931217, 15.068783068783068, 14.920634920634921, 14.042328042328043, 13.98989898989899]
[7.203007518796992, 9.709273182957393, 11.4937343358396, 15.68421052631579, 21.398496240601503, 25.709273182957393, 34.61244019138756, 33.00751879699248, 32.6265664160401, 32.51629072681704, 30.160401002506266, 29.238095238095237, 21.8796992481203, 20.660287081339714, 24.095238095238095, 20.335839598997495, 12.385964912280702, 12.185463659147869, 11.323308270676693, 7.014354066985646]
[6.698412698412699, 9.82010582010582, 10.507936507936508, 14.656084656084657, 17.66137566137566, 21.502645502645503, 29.414141414141415, 26.70899470899471, 26.465608465608465, 26.666666666666668, 26.666666666666668, 25.3015873015873, 23.037037037037038, 14.88888888888889, 19.29100529100529, 12.751322751322752, 7.767195767195767, 10.063492063492063, 6.7407407407407405, 8.484848484848484]
[6.052910052910053, 9.238095238095237, 10.941798941798941, 14.656084656084657, 16.804232804232804, 23.83068783068783, 30.90909090909091, 29.64021164021164, 30.253968253968253, 30.0, 30.0, 29.703703703703702, 24.719576719576718, 16.696969696969695, 11.291005291005291, 8.878306878306878, 4.465608465608466, 4.391534391534392, 3.111111111111111, 3.212121212121212]
[6.275132275132275, 9.44973544973545, 11.43915343915344, 13.873015873015873, 15.851851851851851, 23.61904761904762, 29.505050505050505, 29.07936507936508, 29.96825396825397, 30.0, 30.0, 30.0, 22.8994708994709, 13.969696969696969, 7.873015873015873, 6.0, 4.8994708994708995, 5.26984126984127, 6.761904761904762, 5.91919191919192]
[6.052910052910053, 9.238095238095237, 10.973544973544973, 16.317460317460316, 21.227513227513228, 28.232804232804234, 30.0, 30.105820105820104, 29.98941798941799, 30.0, 30.0, 30.0, 24.656084656084655, 12.424242424242424, 6.8465608465608465, 6.973544973544974, 8.507936507936508, 5.597883597883598, 10.708994708994709, 8.93939393939394]
[6.518518518518518, 9.576719576719576, 10.783068783068783, 16.16931216931217, 22.656084656084655, 27.746031746031747, 30.0, 30.021164021164022, 30.0, 30.0, 30.0, 29.862433862433864, 23.873015873015873, 12.363636363636363, 7.1534391534391535, 6.063492063492063, 7.904761904761905, 6.476190476190476, 6.497354497354498, 10.616161616161616]
[8.402116402116402, 9.619047619047619, 12.19047619047619, 17.142857142857142, 24.52910052910053, 27.873015873015873, 29.96969696969697, 30.0, 30.0, 30.0, 30.0, 28.571428571428573, 22.232804232804234, 12.646464646464647, 7.597883597883598, 6.0, 6.0, 6.8465608465608465, 8.126984126984127, 4.7272727272727275]
[9.365079365079366, 9.798941798941799, 14.031746031746032, 16.105820105820104, 22.952380952380953, 25.047619047619047, 26.333333333333332, 26.444444444444443, 26.444444444444443, 26.444444444444443, 26.444444444444443, 25.365079365079364, 19.26984126984127, 12.181818181818182, 8.814814814814815, 6.6878306878306875, 6.814814814814815, 6.835978835978836, 8.201058201058201, 6.222222222222222]"""





#5 Travail sur les pôles

t_total=1000000
k=10000


def intervalle_temps(t_total,k):
    return t_total/k



def deplacement_aléatoire(i_sortie,j_sortie,carte_pression):
    """Entrée: les indices de la case de sortie de la quantité de matière
       Sortie: la distance entre le point d'entrée et le bord de la carte et les indices de la case d'entrée"""
    distance=random.randint(0,largeur_carte)
    hauteur_case,largeur_case=taille_case(carte_pression)
    distance_totale=largeur_case * i_sortie + distance    #distance par rapport au bord
    if distance_totale>largeur_carte:
        distance_totale=distance_totale - largeur_carte
        i_entrée=distance_totale//largeur_case
    else:
       i_entrée=distance_totale//largeur_case
    if distance_totale<i_sortie*largeur_case:
        distance= -distance       #On prend en compte le fait que la molecule peut se deplacer vers la gauche
    return distance, i_entrée, j_sortie


def temps_aléatoire(v_init_x,distance):
    """Entrée: la distance entre le point de sortie est d'entrée et la vitesse de sortie selon x
       Sortie: le temps aléatoire pour lequel la particule ressort du pôle"""
    temps_min=abs(distance)/abs(v_init_x)
    temps_min += random.randint(0,int(temps_min))   #On met un int car ne marche pas avec un float
    return temps_min

i=4
j=2
dist,i_entrée_elementaire, j_sortie_elementaire=deplacement_aléatoire(i,j,matrice_type)
t_sortie_elementaire=temps_aléatoire(matrice_vitesse_x_apres[i][j],dist)

#dist=6069401, i_entrée_elementaire=4.0, j_sortie_elementaire=2
#t_sortie_elementaire=1091319609267.9999


def arrondie_temps(t,dt):
    """Entrée: un temps, dt
       Sortie: le nombre de dt nécessaire pour atteindre t"""
    return int(dt*(t//dt))


t_sortie_elementaire_final=arrondie_temps(t_sortie_elementaire,t_total/k)

#1091319609200


def transition_position_élémentaire(v_init_x,v_init_y,t_initial,i_sortie,j_sortie,n,liste,carte_pression):
    """Entrée: la vitesse de sortie du groupe de particules, le temps où l'on fait ce passage, les indices de sortie du bloc de particule, la quantité de particule élémentaire, la liste à l'instant t des éléments dans les pôles qui doivent être renvoyé. Cette liste est trié selon les temps. [i,j,t,v_x,v_y,n]
    Sortie: la liste à l'instant t + dt triée"""
    taille_liste=len(liste)
    distance,i_entrée,j_entrée=deplacement_aléatoire(i_sortie,j_sortie,carte_pression)
    element=[i_entrée, j_entrée,t_initial + arrondie_temps(temps_aléatoire(v_init_x,distance), t_total/k),v_init_x, -v_init_y,n]    #Information sur l'element de matière considéré
    liste.append(element)
    return liste


pas_elementaire=transition_position_élémentaire(2,4,100,2,4,10,[[1,2,10,15,12,30]],matrice_type)
# [[1, 2, 10, 15, 12, 30], [1.0, 4, 31919600, 2, -4, 10]]
