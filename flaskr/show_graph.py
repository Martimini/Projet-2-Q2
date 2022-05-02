from fullmoon import IsFullMoon
import numpy as np
from PIL import Image
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flaskr.db import get_db

bp = Blueprint('graph', __name__, url_prefix='/graph')

def isSmaller(date, date2):
    """
    jour/mois/année
    :return: true si date apparait plus tôt dans l'annéée
    """
    parsed_date = date.split('/')
    parsed_date2 = date2.split('/')
    for i in range(1, 4):
        if int(parsed_date[-i]) != int(parsed_date2[-i]):
            return int(parsed_date[-i]) < int(parsed_date2[-i])
    return None

# Les deux fonctions get_graph_lune() et get_graph_velage() sont extrêment similaire c'est pourquoi c'est en cours
# de projet de les rassemblé sous une seule et même fonction qui prend en input la fonction calculatrice
# Par manque de temps cela n'est pas encore fait et sera après les premières review
@bp.route('/graphs_lune', methods=('GET', 'POST'))
def get_graph_lune():
    """
    :return: HTML page with data as parameters
    """
    date_debut = request.form['date_debut']
    date_fin = request.form['date_fin']
    famille = request.form['famille']

    db = get_db()
    data = db.execute('SELECT date, id FROM velages')
    if famille is None:
        dic = lune(data, date_debut, date_fin)
    else:
        validated_data = []
        for i in data:
            animal_id = db.execute('SELECT animal_id FROM animaux_velages WHERE velage_id = ?'), (i[1],)
            famille_id = db.execute('SELECT famille_id FROM animaux WHERE id = ?'), (animal_id,)
            famille_nom = db.execute('SELECT nom FROM familles WHERE id = ?'), (famille_id,)
            if famille_nom == famille:
                validated_data.append(i)
        dic = lune(validated_data, date_debut, date_fin)

    keys = dic.keys()
    values = dic.values()
    error = "Aucune donnée" if dic == {} else None
    if error is None:
        label = "Période"
        # TODO : afficher le graph avec le dic
        return render_template('graph.html', keys=keys, values=values, name=label)
    else: flash(error)
    return redirect(url_for('accueil'))

#  attention package fullmoon utilisé
def lune(date_and_id, debut, fin):
    """
    :param date_and_id: data from database sorted by get_graph_lune()
    :param debut and fin : date between what you're searching for birth day/month/year
    :return: dictionnary {'Pleine Lune':id of animals borned under a fullmoonn, 'Lune incomplète':rest of the animals}
    """
    mooned = []
    unmooned = []
    i = IsFullMoon()
    for row in date_and_id:
        id = row[1]
        date = row[0]
        if not (isSmaller(debut, date) and isSmaller(date, fin)): continue
        if i.set_date_string(date, '%d/%m/%Y').is_full_moon():
            mooned.append(id)
        else: unmooned.append(id)
    return {'Pleine Lune':mooned, 'Lune incomplète':unmooned}

@bp.route('/graphs_velage', methods=('GET', 'POST'))
def get_graph_velage():
    """
    :return: HTML page with data as parameters
    """
    date_debut = request.form['date_debut']
    date_fin = request.form['date_fin']
    famille = request.form['famille']
    db = get_db()
    data = db.execute('SELECT date, id FROM velages')
    if famille is None:
        dic = velages(data, date_debut, date_fin)
    else:
        validated_data = []
        for i in data:
            animal_id = db.execute('SELECT animal_id FROM animaux_velages WHERE velage_id = ?'), (i[1],)
            famille_id = db.execute('SELECT famille_id FROM animaux WHERE id = ?'), (animal_id,)
            famille_nom = db.execute('SELECT nom FROM familles WHERE id = ?'), (famille_id,)
            if famille_nom == famille:
                validated_data.append(i)
        dic = velages(validated_data, date_debut, date_fin)
    keys = dic.keys()
    values = dic.values()
    error = "Aucune donnée" if dic == {} else None
    if error is None:
        label = "Période"
        return render_template('graph.html', keys=keys, values=values, name=label)
    else:
        flash(error)
    return redirect(url_for('accueil'))

def velages(date_and_id, debut, fin):
    """
    :param date_and_id: data from database sorted by get_graph_velages()
    :param debut and fin : date between what you're searching for birth day/month/year
    :return: dictionnary with date as key and number of birth at these date as value of the keys
    """
    counting = {}
    for row in date_and_id:
        date = row[0]
        ID = row[1]
        if isSmaller(debut,date) and isSmaller(date,fin):
            counting[date] = counting.get(date, 0) + 1
    return counting

@bp.route('/graphs_races', methods=('GET', 'POST'))
def get_graph_races():
    """
    :return: HTML page with data as parameters
    """
    races = request.form['races']
    pourcentage = request.form['pourcentage']

    db = get_db()
    data = db.execute('SELECT pourcentage, type_id FROM animaux_types')
    dic = show_races(data, races, pourcentage)
    keys = dic.keys()
    values = dic.values()
    error = "Aucune donnée" if dic == {} else None
    if error is None:
        label = "Races"
        # TODO : afficher le graph avec le dic
        return render_template('graph.html', keys=keys, values=values, name=label)
    else:
        flash(error)
    return redirect(url_for('accueil'))

def show_races(pourcentage_and_races, races:tuple, pourcentage):
    """
    :param pourcentage_and_races: data from get_graph_races()
    :param races: wanted races
    :param pourcentage: minimum pourcentage accepted
    :return: dictionnary number of animals with enough pourcentage of a race as value and the races in question as key
    """
    counting_race = {}
    for row in pourcentage_and_races:
        if float(row[0]) >= pourcentage and row[1] in races:
            counting_race[row[1]] = counting_race.get(row[1],0) + 1
    return counting_race