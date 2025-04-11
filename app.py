from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
import pymysql, pymysql.cursors
from flask_bcrypt import Bcrypt
import random


app = Flask(__name__)
app.secret_key = 'cle_secrete'  # Remplacez par une clé secrète forte
bcrypt = Bcrypt(app)

# fonction pour faciliter la récupération de la connnexion à la base de données
def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='******',  # A remplacer par le mot de passe de votre base de données
        db='ecommerce_db',
        charset='utf8mb4'
    )
    return conn

# -----------------------
# 1. Page d'accueil (index.html)
# -----------------------
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor) 
    # Ici on sélectionne par exemple les 4 derniers produits ajoutés pour les afficher en vedette
    cursor.execute("SELECT * FROM Produits ORDER BY date_ajout DESC LIMIT 4")
    featured_products = cursor.fetchall()
    cursor.close()
    conn.close()
    # La page index.html pourra ainsi itérer sur les produits en vedette récupérés 'featured_products'
    return render_template("index.html", featured_products=featured_products)

# --------------------------------------------------------------------------
# 2. Fonctionnalités pour la Page du Catalogue des produits (produits.html)
# --------------------------------------------------------------------------
@app.route("/produits")
def produits():
    # Récupération des filtres envoyés par GET
    genre = request.args.get("genre")            # Pour filtrer sur le genre
    search = request.args.get("search")            # Pour le champ de recherche
    price_max = request.args.get("price_max")      # Pour filtrer sur le prix maximum
    taille = request.args.get("taille")            # Pour filtrer sur une taille donnée
    couleur = request.args.get("couleur")          # Pour filtrer sur une couleur donnée
    sort_by = request.args.get("sort_by", "newest")  # Critère de tri avec "newest" par défaut

    page = request.args.get("page", 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Appel de la procédure pour récupérer les produits filtrés, paginés et triés
    cursor.callproc("RecupererProduitsFiltres", (genre, search, price_max, taille, couleur, per_page, offset, sort_by))
    products = cursor.fetchall()
    
    # Récupération du nombre total de produits filtrés pour la pagination
    cursor.close()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.callproc("CompterProduitsFiltres", (genre, search, price_max, taille, couleur))
    total = cursor.fetchone()['total']
    
    cursor.close()
    conn.close()
    
    return render_template("produits.html", products=products, total=total, page=page, per_page=per_page)





# on récupère le produit sélectionné et les avis liés à ce produit
@app.route("/produit/<int:produit_id>")
@app.route("/produit/<int:produit_id>")
def produit_detail(produit_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Récupération du produit
    cursor.execute("SELECT * FROM Produits WHERE id_produit = %s", (produit_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close()
        conn.close()
        abort(404)
    
    # Récupération de la note moyenne via la fonction SQL
    cursor.execute("SELECT CalculerMoyenneNotes(%s) AS note_moyenne", (produit_id,))
    result = cursor.fetchone()
    product["note_moyenne"] = result["note_moyenne"] if result and result.get("note_moyenne") is not None else 0

    # Récupération des avis avec jointure sur Utilisateurs pour avoir prenom et nom
    cursor.execute("""
      SELECT Avis.*, Utilisateurs.prenom, Utilisateurs.nom 
      FROM Avis 
      JOIN Utilisateurs ON Avis.id_user = Utilisateurs.id_user 
      WHERE Avis.id_produit = %s 
      ORDER BY date_avis DESC
    """, (produit_id,))
    reviews = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Calcul de my_review dans le code Python (en dehors du template)
    my_review = None
    if session.get('user'):
        for review in reviews:
            # Il est important que les types soient identiques (si besoin, convertissez en int)
            if review['id_user'] == session.get('user')['id_user']:
                my_review = review
                break

    return render_template("detail-produit.html", product=product, reviews=reviews, my_review=my_review)




# fonctionnalité pour l'ajout d'un avis
@app.route("/ajouter-avis/<int:produit_id>", methods=["POST"])
def ajouter_avis(produit_id):
    if "user" not in session:
        flash("Veuillez vous connecter pour laisser un avis.")
        return redirect(url_for("connexion"))

    # Récupération des données du formulaire
    avis_text = request.form.get("avis")
    note = request.form.get("note")
    user_id = session["user"]["id_user"]

    # Connexion et insertion dans la table Avis (selon la structure de la table)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Modification effectuée : utilisation de "commentaire" et "id_user"
        query = "INSERT INTO Avis (id_produit, id_user, note, commentaire, date_avis) VALUES (%s, %s, %s, %s, NOW())"
        cursor.execute(query, (produit_id, user_id, note, avis_text))
        conn.commit()
        flash("Votre avis a été ajouté avec succès !")
    except Exception as e:
        conn.rollback()
        flash("Erreur lors de l'ajout de l'avis : " + str(e))
    finally:
        cursor.close()
        conn.close()

    # Redirection vers la page de détail du produit après l'ajout de l'avis
    return redirect(url_for("produit_detail", produit_id=produit_id))

# Endpoint pour modifier un avis existant
@app.route("/modifier-avis/<int:produit_id>", methods=["GET", "POST"])
def modifier_avis(produit_id):
    if "user" not in session:
        flash("Veuillez vous connecter pour modifier votre avis.")
        return redirect(url_for("connexion"))
    
    user_id = session["user"]["id_user"]
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # Récupération de l'avis existant de l'utilisateur pour ce produit
    cursor.execute("SELECT * FROM Avis WHERE id_produit = %s AND id_user = %s", (produit_id, user_id))
    review = cursor.fetchone()
    if not review:
        flash("Aucun avis trouvé à modifier.")
        cursor.close()
        conn.close()
        return redirect(url_for("produit_detail", produit_id=produit_id))
    
    if request.method == "POST":
        new_avis_text = request.form.get("avis")
        new_note = request.form.get("note")
        try:
            query = "UPDATE Avis SET commentaire = %s, note = %s, date_avis = NOW() WHERE id_avis = %s"
            cursor.execute(query, (new_avis_text, new_note, review["id_avis"]))
            conn.commit()
            flash("Votre avis a été modifié avec succès.")
        except Exception as e:
            conn.rollback()
            flash("Erreur lors de la modification de l'avis : " + str(e))
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("produit_detail", produit_id=produit_id))
    
    cursor.close()
    conn.close()
    # Affichage du formulaire de modification pré-rempli avec les données existantes
    return render_template("modifier-avis.html", produit_id=produit_id, review=review)


# -----------------------------------------------
# Route d'inscription
# -----------------------------------------------
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        # Récupération des valeurs du formulaire
        first_name = request.form.get("first-name")
        last_name = request.form.get("last-name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        address = request.form.get("address")
        postal_code = request.form.get("postal-code")
        city = request.form.get("city")
        phone = request.form.get("phone")
        terms = request.form.get("terms")
        newsletter = request.form.get("newsletter")  # Facultatif
        
        # Vérifications basiques
        if not all([first_name, last_name, email, password, confirm_password, address, postal_code, city, phone]):
            flash("Tous les champs sont obligatoires.")
            return redirect(url_for("inscription"))
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.")
            return redirect(url_for("inscription"))
        if not terms:
            flash("Vous devez accepter les conditions générales.")
            return redirect(url_for("inscription"))
        
        # Hachage du mot de passe avec Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insertion dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insertion dans la table Utilisateurs
            query = "INSERT INTO Utilisateurs (nom, prenom, email, mdp, type) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (last_name, first_name, email, hashed_password, "Client"))
            user_id = cursor.lastrowid

            # Combiner les informations d'adresse en une seule chaîne
            full_address = f"{address}, {postal_code}, {city}. Téléphone : {phone}"
            query_client = "INSERT INTO Clients (id_user, adresse) VALUES (%s, %s)"
            cursor.execute(query_client, (user_id, full_address))
            
            conn.commit()
            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.")
            return redirect(url_for("connexion"))
        except Exception as e:
            conn.rollback()
            flash("Erreur lors de l'inscription : " + str(e))
            return redirect(url_for("inscription"))
        finally:
            cursor.close()
            conn.close()
    return render_template("inscription.html")


# -----------------------------------------------
# Route de connexion
# -----------------------------------------------
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Vérification que tous les champs sont fournis
        if not email or not password:
            flash("Veuillez remplir tous les champs.")
            return redirect(url_for("connexion"))
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM Utilisateurs WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Vérification du mot de passe avec Bcrypt
        if user and bcrypt.check_password_hash(user["mdp"], password):
            session["user"] = user  # Stocker l'utilisateur dans la session
            flash("Connexion réussie!")
            return redirect(url_for("index"))
        else:
            flash("Email ou mot de passe incorrect.")
            return redirect(url_for("connexion"))
            
    return render_template("connexion.html")

# -----------------------------------------------
# Route de déconnexion
# -----------------------------------------------

@app.route("/deconnexion")
def deconnexion():
    session.pop("user", None)
    flash("Vous êtes maintenant déconnecté.")
    return redirect(url_for("index"))

# -----------------------------------------------
# Route panier
# -----------------------------------------------

# procédure d'ajout dans le panier 
@app.route("/ajouter-panier", methods=["POST"])
def ajouter_panier():
    # Vérifier que l'utilisateur est connecté
    if "user" not in session:
        flash("Veuillez vous connecter pour ajouter des articles à votre panier.")
        return redirect(url_for("connexion"))
    user_id = session["user"]["id_user"]

    # Récupérer l'id du produit et la quantité depuis le formulaire
    product_id = request.form.get("product_id")
    quantite = request.form.get("quantite", 1, type=int)
    
    if not product_id or quantite < 1:
        flash("Paramètres invalides.")
        return redirect(url_for("produit_detail", produit_id=product_id))
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Recherche d'un panier actif pour l'utilisateur
    cursor.execute("SELECT * FROM Paniers WHERE id_user = %s AND statut = 'actif'", (user_id,))
    panier = cursor.fetchone()
    
    if panier is None:
        # Création d'un nouveau panier
        cursor.execute("INSERT INTO Paniers (id_user, statut) VALUES (%s, 'actif')", (user_id,))
        conn.commit()
        panier_id = cursor.lastrowid
    else:
        panier_id = panier["id_panier"]
    
    # Vérifier si le produit existe déjà dans le panier
    cursor.execute("SELECT * FROM Panier_Produits WHERE id_panier = %s AND id_produit = %s", (panier_id, product_id))
    item = cursor.fetchone()
    if item is None:
        # Insérer le produit dans le panier
        cursor.execute("INSERT INTO Panier_Produits (id_panier, id_produit, quantite) VALUES (%s, %s, %s)", 
                       (panier_id, product_id, quantite))
    else:
        # Mettre à jour la quantité
        cursor.execute("UPDATE Panier_Produits SET quantite = quantite + %s WHERE id_panier = %s AND id_produit = %s", 
                       (quantite, panier_id, product_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Produit ajouté au panier avec succès!")
    return redirect(url_for("panier"))


# Cette route charge le panier actif de l'utilisateur connecté, joint les articles avec les informations produit et calcule le récapitulatif
@app.route("/panier")
def panier():
    if "user" not in session:
        flash("Veuillez vous connecter pour accéder à votre panier.")
        return redirect(url_for("connexion"))
    user_id = session["user"]["id_user"]
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Récupération du panier actif
    cursor.execute("SELECT * FROM Paniers WHERE id_user = %s AND statut = 'actif'", (user_id,))
    panier = cursor.fetchone()
    
    cart_items = []
    subtotal = 0.0
    if panier:
        panier_id = panier["id_panier"]
        # Récupérer les articles du panier avec les infos du produit
        query = """
            SELECT pp.quantite, p.*
            FROM Panier_Produits pp
            JOIN Produits p ON pp.id_produit = p.id_produit
            WHERE pp.id_panier = %s
        """
        cursor.execute(query, (panier_id,))
        cart_items = cursor.fetchall()
        # Calcul du sous-total
        for item in cart_items:
            subtotal += item["quantite"] * float(item["prix"])
    
    cursor.close()
    conn.close()
    
    # Pour l'exemple, on fixe des frais de livraison et on calcule la TVA à 20%
    shipping_cost = 4.99 if subtotal > 0 else 0.0
    tax = subtotal * 0.20
    total = subtotal + shipping_cost + tax
    return render_template("panier.html", cart_items=cart_items, subtotal=subtotal, shipping_cost=shipping_cost, tax=tax, total=total)


# -----------------------------------------------
# 7. Workflow Commande, Paiement et Confirmation
# -----------------------------------------------

# Étape 1 : Informations de livraison et création de commande (commande.html)
@app.route("/commande", methods=["GET", "POST"])
def commande():
    if "user" not in session:
        flash("Veuillez vous connecter pour finaliser votre commande.")
        return redirect(url_for("connexion"))
    
    user_id = session["user"]["id_user"]
    
    if request.method == "POST":
        shipping_info = {
            "first_name": request.form.get("first-name"),
            "last_name": request.form.get("last-name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "address2": request.form.get("address2"),
            "postal_code": request.form.get("postal-code"),
            "city": request.form.get("city"),
            "country": request.form.get("country"),
            "shipping_method": request.form.get("shipping-method"),
            "order_notes": request.form.get("order-notes")
        }
        session["shipping_info"] = shipping_info

        # Récupérer le panier actif
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM Paniers WHERE id_user = %s AND statut = 'actif'", (user_id,))
        panier = cursor.fetchone()
        if not panier:
            flash("Aucun panier actif trouvé.")
            return redirect(url_for("panier"))
        panier_id = panier["id_panier"]
        
        # Créer la commande en insérant une nouvelle ligne dans la table Commandes
        cursor.execute("INSERT INTO Commandes (id_user, id_panier, date_commande, statut) VALUES (%s, %s, NOW(), 'en attente')", (user_id, panier_id))
        id_commande = cursor.lastrowid
        
        # Mettre à jour le statut du panier pour marquer qu'il est validé
        cursor.execute("UPDATE Paniers SET statut = 'validé' WHERE id_panier = %s", (panier_id,))
        
        # Insérer les informations de livraison dans la table Livraisons
        cursor.execute(
            "INSERT INTO Livraisons (id_commande, adresse, code_postal, ville, pays, telephone, mode_livraison) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (id_commande, shipping_info["address"], shipping_info["postal_code"], shipping_info["city"], shipping_info["country"], shipping_info["phone"], shipping_info["shipping_method"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Stocker l'id de la commande dans la session pour la suite
        session["id_commande"] = id_commande
        return redirect(url_for("paiement"))
    
    # Pour un GET, calculer et afficher le récapitulatif du panier
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Paniers WHERE id_user = %s AND statut = 'actif'", (user_id,))
    panier = cursor.fetchone()
    cart_items = []
    subtotal = 0.0
    if panier:
        panier_id = panier["id_panier"]
        query = """
            SELECT pp.quantite, p.*
            FROM Panier_Produits pp
            JOIN Produits p ON pp.id_produit = p.id_produit
            WHERE pp.id_panier = %s
        """
        cursor.execute(query, (panier_id,))
        cart_items = cursor.fetchall()
        for item in cart_items:
            subtotal += item["quantite"] * float(item["prix"])
    cursor.close()
    conn.close()
    
    shipping_cost = 4.99 if subtotal > 0 else 0.0
    tax = subtotal * 0.20
    total = subtotal + shipping_cost + tax
    
    return render_template("commande.html",
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping_cost=shipping_cost,
                           tax=tax,
                           total=total)

# Étape 2 : Paiement (paiement.html)
@app.route("/paiement", methods=["GET", "POST"])
def paiement():
    if "user" not in session or "shipping_info" not in session or "id_commande" not in session:
        flash("Veuillez compléter vos informations de livraison.")
        return redirect(url_for("commande"))
    
    # Pour obtenir le montant total, recalculons-le à partir du panier de la commande validée
    user_id = session["user"]["id_user"]
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Paniers WHERE id_user = %s AND statut = 'validé'", (user_id,))
    panier = cursor.fetchone()
    subtotal = 0.0
    if panier:
        panier_id = panier["id_panier"]
        query = """
            SELECT pp.quantite, p.prix
            FROM Panier_Produits pp
            JOIN Produits p ON pp.id_produit = p.id_produit
            WHERE pp.id_panier = %s
        """
        cursor.execute(query, (panier_id,))
        items = cursor.fetchall()
        for item in items:
            subtotal += item["quantite"] * float(item["prix"])
    cursor.close()
    conn.close()
    
    shipping_cost = 4.99 if subtotal > 0 else 0.0
    tax = subtotal * 0.20
    total = subtotal + shipping_cost + tax
    
    if request.method == "POST":
        payment_method = request.form.get("payment_method")
        # Simulation du paiement avec 90% de succès
        if random.random() < 0.9:
            payment_status = "réussi"
        else:
            payment_status = "échec"
        
        # Insérer l'enregistrement du paiement dans la table Paiements
        id_commande = session.get("id_commande")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Paiements (id_commande, montant, methode, statut, date_paiement) VALUES (%s, %s, %s, %s, NOW())",
            (id_commande, total, payment_method, payment_status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        session["payment_info"] = {"payment_method": payment_method, "status": payment_status}
        
        if payment_status == "réussi":
            flash("Paiement effectué avec succès!")
            return redirect(url_for("confirmation"))
        else:
            flash("Erreur lors du paiement. Veuillez réessayer.")
            return redirect(url_for("paiement"))
    
    return render_template("paiement.html", total=total)

# Étape 3 : Confirmation (confirmation.html)
@app.route("/confirmation")
def confirmation():
    if "user" not in session or "shipping_info" not in session or "payment_info" not in session or "id_commande" not in session:
        flash("Commande incomplète.")
        return redirect(url_for("commande"))
    
    shipping_info = session.get("shipping_info")
    payment_info = session.get("payment_info")
    
    # Ici, vous pourriez, par exemple, récupérer la commande finalisée depuis la DB en utilisant l'id_commande
    id_commande = session.get("id_commande")
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Commandes WHERE id_commande = %s", (id_commande,))
    commande = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template("confirmation.html", shipping_info=shipping_info, payment_info=payment_info, commande=commande)


# -----------------------------------------------
# Route suivi commandes
# -----------------------------------------------
@app.route("/suivi_commandes")
def suivi_commandes():
    if "user" not in session:
        flash("Vous devez être connecté pour suivre vos commandes.")
        return redirect(url_for("connexion"))
    
    user_id = session["user"]["id_user"]
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query = """
        SELECT c.id_commande, c.date_commande, c.statut, 
               l.adresse, l.code_postal, l.ville, l.pays, l.telephone, l.mode_livraison,
               p.statut AS paiement_statut
        FROM Commandes c
        JOIN Livraisons l ON c.id_commande = l.id_commande
        LEFT JOIN Paiements p ON c.id_commande = p.id_commande
        WHERE c.id_user = %s
        ORDER BY c.date_commande DESC
    """
    cursor.execute(query, (user_id,))
    orders = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("suivi-commande.html", orders=orders)


# -----------------------------------------------
# Route details-commandes
# -----------------------------------------------
@app.route("/details_commande/<int:id_commande>")
def details_commande(id_commande):
    if "user" not in session:
        flash("Vous devez être connecté pour consulter les détails de la commande.")
        return redirect(url_for("connexion"))
    
    user_id = session["user"]["id_user"]
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query_order = """
       SELECT c.id_commande, c.date_commande, c.statut AS commande_statut,
              l.adresse, l.code_postal, l.ville, l.pays, l.telephone, l.mode_livraison,
              p.statut AS paiement_statut, p.methode, p.date_paiement, p.montant
       FROM Commandes c
       JOIN Livraisons l ON c.id_commande = l.id_commande
       LEFT JOIN Paiements p ON c.id_commande = p.id_commande
       WHERE c.id_commande = %s AND c.id_user = %s
    """
    cursor.execute(query_order, (id_commande, user_id))
    order = cursor.fetchone()
    if not order:
        flash("Commande introuvable.")
        return redirect(url_for("suivi_commandes"))
    
    query_items = """
       SELECT pp.quantite, pr.nom, pr.prix, pr.description
       FROM Panier_Produits pp
       JOIN Produits pr ON pp.id_produit = pr.id_produit
       WHERE pp.id_panier = (SELECT id_panier FROM Commandes WHERE id_commande = %s)
    """
    cursor.execute(query_items, (id_commande,))
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("details-commande.html", order=order, items=items)





if __name__ == "__main__":
    app.run(debug=True)


