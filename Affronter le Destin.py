print("alakazoum...")

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
from datetime import datetime
import time



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

def multScalVect2 (l, v):
    return Vect2((l*v[0], l*v[1]))

VectNul = Vect2( (0, 0) )

def transposerMat(mat):
    n, m = len(mat), len(mat[0])
    rep = []
    for j in range(m):
        rep.append([mat[0][0]]*n)
        for i in range(n):
            rep[j][i] = mat[i][j]
    return rep

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def getColor(t):
    t = max(0, min(1, t))
    return rgb_hack( ((1-t)*color0[0]+t*colorMax[0], (1-t)*color0[1]+t*colorMax[1], (1-t)*color0[2]+t*colorMax[2]) )

def rgb_hack(rgb):
    rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return "#%02x%02x%02x" % rgb



#================================================================

#ALERT !!
#Les coord de mes Cell sont TOUJOURS celles de son CENTRE (et pas celles de son coin bas gauche)
#ALERT !!

#On travaille en radians et en mètres
#le point de coordonées 0,0 se trouve en long = 0, lat = -latitudeMaxPoles
#la case d'indice 0, 0 se trouve en long = 0, lat = -latitudeMaxPoles


#constantes physiques
rayonTerre = 6.371e6
masse_mol_soufre = (2*16+32)*10**-3    #SO_2 est l'élément considéré
masse_vol_air=0.0135   #en kg/m-3
timeNOW = 0

#constantes relatives à la carte
#suseptibles d'être changées
largeurMondeCell  = 60# nombre de Cells en largeur  (en Y)
longueurMondeCell = 150 #nombre de Cells en longueur (en X)

#on se place au level 80
#donc



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



#intervalle temps
t_total= 3.154e+7
k=100

dt = t_total/k

#constante calcul pression
constante=4.7*10**(-3)  #Constante  calculé dans la démo de la fonction passage_temperature_sol_pression(M,Tsol) dans l'open office
P0=100000
altitude=9000   #La température ne varie pas entre 9 et 20 km (à peu près)
g=9.81
R=8.31




tkLongueurCell = 7 #(en pixel, uniquement pour le dessin)
tkLargeurCell = 7 #(en pixel, uniquement pour le dessin)
tkOffsetX = 100
tkOffsetY = 100
tkTailleVect = 15


def taille_case():
    """Prend la carte de pression et renvoie la taille réel des cases en m (hauteur de la case, largeur de la case)"""
    return largeurCell,longueurCell

root = tk.Tk()
root.geometry("1280x1024")
root.title('Youpi ?')

canvas = tk.Canvas(root,bg='white', width = 1280,height = 1024)
textDate = StringVar()
label = Label(root, textvariable=textDate, relief=RAISED)

#Couleurs tkinter
#couleur quand il n'y a pas de soufre
color0 = (255, 255, 255)

#couleur quand il y a satSoufre ou plus
colorMax = (255, 70, 35)
satSoufre = 100#au pif pour l'instant


#----------------------
print("Constantes + import ok !")


Image1 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.21.05.2022.PNG" )
image_array1 = np.asarray( Image1 )    #asarray pour empecher la modification de l'image

Image2 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.22.05.2022.PNG" )
image_array2 = np.asarray( Image2 )    #asarray pour empecher la modification de l'image

Image3 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.23.05.2022.PNG" )
image_array3 = np.asarray( Image3 )    #asarray pour empecher la modification de l'image

Image4 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.24.05.2022.PNG" )
image_array4 = np.asarray( Image4 )    #asarray pour empecher la modification de l'image

Image5 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.25.05.2022.PNG" )
image_array5 = np.asarray( Image5 )    #asarray pour empecher la modification de l'image

Image6 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.26.05.2022.PNG" )
image_array6 = np.asarray( Image6 )    #asarray pour empecher la modification de l'image

Image7 = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Carte TIPE\Capture.27.05.2022.PNG" )
image_array7 = np.asarray( Image7 )    #asarray pour empecher la modification de l'image


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



#température=np.zeros(6)
#température=température.reshape(2,3)



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

print("Image Pixel ok !")

#matrice_temp_couleur=passage_carte_couleur_carte_température(matrice_couleur)

#verification: la commande passage_carte_couleur_carte_température(matrice_couleur) renvoie:
#array([[42., 42., 46.],
 #      [26., 18., 22.]])


# matrice1=passage_carte_couleur_carte_température(image_array1)
# 
# with open('matrice1.txt','w') as f1:
#     json.dump(matrice1.tolist(),f1)
# 
# print("matrice1 ok!")
# 
# matrice2=passage_carte_couleur_carte_température(image_array2)
# 
# with open('matrice2.txt','w') as f2:
#     json.dump(matrice2.tolist(),f2)
# 
# print("matrice2 ok!")
# 
# matrice3=passage_carte_couleur_carte_température(image_array3)
# 
# with open('matrice3.txt','w') as f3:
#     json.dump(matrice3.tolist(),f3)
# 
# print("matrice3 ok!")
# 
# matrice4=passage_carte_couleur_carte_température(image_array4)
# 
# with open('matrice4.txt','w') as f4:
#     json.dump(matrice4.tolist(),f4)
# 
# print("matrice4 ok!")
# 
# matrice5=passage_carte_couleur_carte_température(image_array5)
# 
# with open('matrice5.txt','w') as f5:
#     json.dump(matrice5.tolist(),f5)
# 
# print("matrice5 ok!")
# 
# matrice6=passage_carte_couleur_carte_température(image_array6)
# 
# with open('matrice6.txt','w') as f6:
#     json.dump(matrice6.tolist(),f6)
# 
# print("matrice6 ok!")
# 
# matrice7=passage_carte_couleur_carte_température(image_array7)
# 
# with open('matrice7.txt','w') as f7:
#     json.dump(matrice7.tolist(),f7)
# 
# print("matrice7 ok!")

f = open("matrice1.txt")
matrice1 = np.array(json.load(f))

f = open("matrice2.txt")
matrice2 = np.array(json.load(f))

f = open("matrice3.txt")
matrice3 = np.array(json.load(f))

f = open("matrice4.txt")
matrice4 = np.array(json.load(f))

f = open("matrice5.txt")
matrice5 = np.array(json.load(f))

f = open("matrice6.txt")
matrice6 = np.array(json.load(f))

f = open("matrice7.txt")
matrice7 = np.array(json.load(f))
#matrice[120]

print("matrice temp ok !")

#définition de Carte et Cell, soit le "meat and potatoes" de la simulation


#Travail Théo

class Cell:

    def __init__(self, estUnPole, masse, i, j, taille = Vect2((longueurCell, largeurCell))):

        self.estUnPole = estUnPole
        
        if estUnPole:
            #vraies variables
            self.ls = []
            
            #Variables qui ne servent à rien
            #juste à éviter des ErrorNotFound quand on importe
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
        
        self.maxVitesse = 1

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
            indX = int(x//longueurCell) % longueurMondeCell
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
            indX = int(longueurCalc//longueurCell) % longueurMondeCell

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

        xinter = longueurCell*(coordCoinDH[0] // longueurCell) #+ coordCoinDH[0] % longueurCell
        yinter = largeurCell*(coordCoinDH[1] // largeurCell) #+ coordCoinDH[1] % largeurCell
        vectInter = Vect2((xinter, yinter))

        aireDH = abs((coordCoinDH - vectInter)[0] * (coordCoinDH - vectInter)[1])
        aireDB = abs((coordCoinDB - vectInter)[0] * (coordCoinDB - vectInter)[1])
        aireGB = abs((coordCoinGB - vectInter)[0] * (coordCoinGB - vectInter)[1])
        aireGH = abs((coordCoinGH - vectInter)[0] * (coordCoinGH - vectInter)[1])        
        #normalement, on a aireDH + ... + aireGH = largeurCell*longueurCell (=A0)

        #print(cellCoinDH.ij, cellCoinDB.ij, cellCoinGB.ij, cellCoinGH.ij)
        #print(aireDH,"+",aireDB,"+",aireGB,"+",aireGH,"=", (aireDH+aireDB+aireGB+aireGH), "et A0 =",A0)
        
        rep = []
        rep.append( (cellCoinDH, aireDH/A0) )
        rep.append( (cellCoinDB, aireDB/A0) )
        rep.append( (cellCoinGB, aireGB/A0) )
        rep.append( (cellCoinGH, aireGH/A0) )
        
        #print(aireDH/A0, aireDB/A0, aireGB/A0, aireGH/A0)

        #donc return [ [cell, float]; [...] ]
        return rep

    #4 Passage de la carte des vitesses de l'instant t à l'instant t+dt
    def accToVitesse(self, cell):
        cell.v += multScalVect2(dt, cell.a)

    def updateCells(self, matriceAccAir):

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                
                cell = self.cells[i][j]
                
                cell.a = Vect2((0, 0))
                cell.a = matriceAccAir[i][j]

                self.accToVitesse(cell)

                #purement graphique
                if dist(cell.v, VectNul) > self.maxVitesse:
                    self.maxVitesse = dist(cell.v, VectNul)
                
                #on retourne dans la partie physique
                destinations = self.cellsFromCellAndCoord(cell)
                #on enlève le soufre dans la case originelle
                m0 = cell.m
                cell.m = 0
                #pour enventuellement le remettre si il ne s'est pas trop déplacé
                for e in destinations:  
                    if e[0].estUnPole:
                        #à remplir
                        e[0].ls += [transition_position_élémentaire(cell.v, timeNOW, j, i, m0*e[1])]
                        #[i,j,t_auquel_il_doit_sortir,v_x,v_y,m]
                            
                    else:
                        e[0].val += m0*e[1]    #on le met dans .val temporairement car on ne peut pas le mettre directement dans .m
                        
        
        #UpdatePoles
        #ne pas oublier que les i de Jb sont mes j et inversement
        indices_a_elim = []
        for l in range(len(self.poleNord.ls)):                                          #[i,j,t_auquel_il_doit_sortir,v_x,v_y,m]
            e = self.poleNord.ls[l]
            if e[2] > timeNOW:
                self.cells[e[1]][e[0]].val += e[5]                          #self.cells[i][j].val += m
                indices_a_elim.append(l)
        
        for p in range(len(indices_a_elim)-1, -1, -1):
            self.poleNord.ls.pop(indices_a_elim[p])
        
        indices_a_elim = []
        for l in range(len(self.poleSud.ls)):                                          #[i,j,t_auquel_il_doit_sortir,v_x,v_y,m]
            e = self.poleSud.ls[l]
            if e[2] > timeNOW:
                self.cells[e[1]][e[0]].val += e[5]                          #self.cells[i][j].val += m
                indices_a_elim.append(l)
                
        for p in range(len(indices_a_elim)-1, -1, -1):
            self.poleSud.ls.pop(indices_a_elim[p])
        

        #vu qu'on avait mis la variation de masse dans .val, on le remets dans .m
        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                cell = self.cells[i][j]
                cell.m = cell.val
                cell.val = 0
       
    def matrice_Pression_pour_Jb(self): 
        #nous donne la matrice des pressions (de la taille longueurMondeCell*largeurMondeCell)
        #C'est juste un recopiage de valeurs
        matRep = []
        for j in range(largeurMondeCell):
            matRep.append([])
            for i in range(longueurMondeCell):
                matRep[j].append(self.cells[i][largeurMondeCell-j-1].pression)
        return matRep
        
    def passageTempPression(self):
        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                c0 = self.cells[i][j]
                c0.pression = P0*((c0.val + 273.15-constante*altitude)/(c0.val+273.15))**(masse_mol_soufre*g/(constante*R))
                c0.val = 0
                
    def getMasseTropique (self):
        angleTropique = radians(23+1/60*26)
        
        cellSud = self.cellFromLatLongRad(-angleTropique, 0)
        cellNord = self.cellFromLatLongRad(angleTropique, 0)
        
        jsud = cellSud.ij[1]
        jnord = cellNord.ij[1]
        
        rep = 0
        
        for i in range(longueurMondeCell):
            for j in range(jsud, jnord+1):
                rep += self.cells[i][j].m
        return rep
            
        

    def draw(self):

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                
                cell = self.cells[i][j]
                
                newColor = getColor(cell.m/satSoufre)
                canvas.create_rectangle( i*tkLongueurCell + tkOffsetX, (largeurMondeCell-j-1)*tkLargeurCell + tkOffsetY, (i+1)*tkLongueurCell+tkOffsetX,  (largeurMondeCell-j)*tkLargeurCell+tkOffsetY, fill=newColor, dash=(1))
                
                #ça marche pas bouhouhou
                #canvas.create_line((i+0.5)*tkLongueurCell + tkOffsetX, (largeurMondeCell-j-0.5)*tkLargeurCell + tkOffsetY, (i+0.5)*tkLongueurCell +cell.v[0]/self.maxVitesse+ tkOffsetX, (largeurMondeCell-j-0.5)*tkLargeurCell +cell.v[1]/self.maxVitesse+ tkOffsetY, dash=(50, 1))
                canvas.pack()
                
                


print("Cells + Carte ok !")  
    
    
    
    
#Passage température globale à température moyennée


def importBigArray(carte0, ba):
    #[temp]

    n = len(ba)
    m = len(ba[0])
    for i in range(longueurMondeCell):
        for j in range(largeurMondeCell):
            if (carte0.cells[i][j].nbData != 0):
                carte0.cells[i][j].val = 0
                carte0.cells[i][j].nbData = 0
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

    
    
    
#Passage température pression

def passage_carte_pression_carte_acceleration_selon_x(masse_volumique,carte_pression):
    """Donne une matrice dont les coordonnées sont les accélérations selon x en ce point de la matrice"""
    n,m=len(carte_pression),len(carte_pression[0])   #Matrice Mn,m(R)
    matrice_1_x=[]
    dx,dy=taille_case()
    for i in range(n):    #travaillons d'abord les coordonnées selon ex
        liste=[]
        for j in range(m-1):
           liste.append((carte_pression[i][j] - carte_pression[i][j+1])/(dx*masse_volumique))    #On ajoute l'acceleration selon ex
        liste.append((carte_pression[i][m-1] - carte_pression[i][0])/(dx*masse_volumique))  #On ajoute l'acceleration selon ex au bord
        matrice_1_x.append(liste)
    matrice_final=[]  #On cherche maintenant à donner les accélérations moyennes entre 2 bords
    for i in range(n):
        liste=[]
        liste.append((matrice_1_x[i][0] + matrice_1_x[i][m-1])/2)   #On travail sur le bord
        for j in range(m-1):
            liste.append((matrice_1_x[i][j] + matrice_1_x[i][j+1])/2)  #(ax1-ax2)/2
        matrice_final.append(liste)
    return matrice_final



def passage_carte_pression_carte_acceleration_selon_y(masse_volumique,carte_pression):
    n,m=len(carte_pression),len(carte_pression[0])   #Matrice Mn,m(R)
    matrice_1_y=[]
    dx,dy=taille_case()
    for i in range(n-1):
        liste=[]
        for j in range(m):    #les bords du haut et du bas ne se rejoignent pas. Cela est traité ailleurs
            liste.append((carte_pression[i][j] - carte_pression[i+1][j])/(dy*masse_volumique))
        matrice_1_y.append(liste)
    matrice_final=[]
    liste=[]
    for j in range(m):
        liste.append(matrice_1_y[0][j])
    matrice_final.append(liste)
    for i in range(n-2):
        liste=[]
        for j in range(m):
            liste.append((matrice_1_y[i][j] + matrice_1_y[i+1][j])/2)
       # liste.append(matrice_1_y[n-2][j])
        matrice_final.append(liste)
    liste=[]
    for j in range(m):
        liste.append(matrice_1_y[n-2][j])
    matrice_final.append(liste)
    return matrice_final

def passage_carte_pression_carte_acceleration_selon_x_et_y (carte_pression):
    matX = passage_carte_pression_carte_acceleration_selon_x(masse_vol_air, carte_pression)
    matY = passage_carte_pression_carte_acceleration_selon_y(masse_vol_air, carte_pression)

    (n, m) = len(matX), len(matX[0])
    mat_fin = []
    for i in range(n):
        mat_fin.append([])
        for j in range(m):
            mat_fin[i].append( (matX[i][j], matY[i][j]) )
        
    return transposerMat(mat_fin)
                                                               
                                                                                                                              

#5 Travail sur les pôles


def deplacement_aléatoire(i_sortie,j_sortie):
    """Entrée: les indices de la case de sortie de la quantité de matière
       Sortie: la distance entre le point d'entrée et le bord de la carte et les indices de la case d'entrée"""
    distance=random.randint(0,longueurMondeCell)
    hauteur_case,largeur_case=taille_case()
    distance_totale=largeur_case * (i_sortie + distance)    #distance par rapport au bord
    if distance_totale>longueurMonde:
        distance_totale=distance_totale - longueurMonde
        i_entrée=distance_totale//largeur_case
    else:
       i_entrée=distance_totale//largeur_case
    if distance_totale<i_sortie*largeur_case:
        distance= -distance       #On prend en compte le fait que la molecule peut se deplacer vers la gauche
    return distance, int(i_entrée)%largeurMondeCell, int(j_sortie)%longueurMondeCell


def temps_aléatoire(v_init_x,distance):
    """Entrée: la distance entre le point de sortie est d'entrée et la vitesse de sortie selon x
       Sortie: le temps aléatoire pour lequel la particule ressort du pôle"""
    
    temps_min=abs(distance)/abs(v_init_x)
    temps_min += random.randint(0,int(temps_min))   #On met un int car ne marche pas avec un float
    return temps_min

#i=4
#j=2
#dist,i_entrée_elementaire, j_sortie_elementaire=deplacement_aléatoire(i,j,matrice_type)
#t_sortie_elementaire=temps_aléatoire(matrice_vitesse_x_apres[i][j],dist)

#dist=6069401, i_entrée_elementaire=4.0, j_sortie_elementaire=2
#t_sortie_elementaire=1091319609267.9999

#1091319609200

def transition_position_élémentaire(v_init,t_initial,i_sortie,j_sortie,m):
    """Entrée: la vitesse de sortie du groupe de particules, le temps où l'on fait ce passage, les indices de sortie du bloc de particule, la quantité de particule élémentaire,
    [i,j,t,v_x,v_y,m]
    Sortie: la liste à l'instant t + dt triée"""
    
    distance,i_entrée,j_entrée=deplacement_aléatoire(i_sortie,j_sortie)
    temps_final = t_initial + temps_aléatoire(abs(v_init[0]) + abs(v_init[1]),distance)
    element=[i_entrée, j_entrée, temps_final, v_init[0], -v_init[1],m]    #Information sur l'element de matière considéré
    
    return element


# pas_elementaire=transition_position_élémentaire(2,4,100,2,4,10,[[1,2,10,15,12,30]],matrice_type)
# [[1, 2, 10, 15, 12, 30], [1.0, 4, 31919600, 2, -4, 10]]

   


                
#fonctions de controle, les mainLoop :

def Update(carte0, carte_pression):
    
    matriceAccAir = passage_carte_pression_carte_acceleration_selon_x_et_y( carte_pression )
    
    carte0.updateCells(matriceAccAir)

def Draw(carte0):
    carte0.draw()
    textDate.set(str(timeNOW))
    label.pack()
    root.update_idletasks()
    root.update()

def animate (carte0):
    
    Draw(carte0)
    
    Update(carte0, carte0.matrice_Pression_pour_Jb())
    
    time.sleep(1.0)
    
print("import + logique poles ok !")
                                                                 
#===========================================================================================================================================================================                                                          
#====================================================================================================================================================================================================
#========================================================================================================================================================================

#on exécute le code ici

#========================================================================================================================================================================
#========================================================================================================================================================================
print("on commence !!!!!!!!!!!")

carte_init=Carte()
importBigArray(carte_init,matrice1)
carte_init.cells[75][30].m += 1000
Draw(carte_init)

indice_max=k
indice=0   
                                                                 
while indice<=indice_max:
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice2)
    indice+=1
    
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice3)
    indice+=1
    
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice4)
    indice+=1
    
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice5)
    indice+=1
    
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice6)
    indice+=1
    
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice7)
    indice+=1
    
    print(indice)
    animate(carte_init)
    print("t =", timeNOW)
    print("qté soufre dans les tropiques = ", carte_init.getMasseTropique())
    timeNOW += dt
    importBigArray(carte_init,matrice1)
    indice+=1
                                                                 

def energie_reflechie(q_init,q_f,C_R):
    percent=q_f/q_init*100
    return((q_init*6.022*10**23*(0.382*10**(-9))**2*C_R)/(64*pi*(6360*10**3)**2))
