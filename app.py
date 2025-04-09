from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
import pymysql, pymysql.cursors
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'cle_secrete'  # Remplacez par une clé secrète forte
bcrypt = Bcrypt(app)

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='********',  # Remplacez par votre mot de passe
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
    # Sélectionner par exemple les 4 derniers produits ajoutés à afficher en vedette
    cursor.execute("SELECT * FROM Produits ORDER BY date_ajout DESC LIMIT 4")
    featured_products = cursor.fetchall()
    cursor.close()
    conn.close()
    # La template index.html pourra itérer sur 'featured_products'
    return render_template("index.html", featured_products=featured_products)

# -----------------------
# 2. Page Catalogue (produits.html)
# -----------------------
@app.route("/produits")
def produits():
    # Récupération des paramètres de filtre et de pagination s'il y a lieu
    categorie = request.args.get("categorie")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    per_page = 12  # nombre de produits par page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Construction de la requête de sélection dynamique
    query = "SELECT * FROM Produits WHERE 1=1"
    params = []
    if categorie:
        query += " AND LOWER(categorie) = LOWER(%s)"
        params.append(categorie)
    if search:
        query += " AND (nom LIKE %s OR description LIKE %s)"
        params.append('%' + search + '%')
        params.append('%' + search + '%')
    query += " LIMIT %s OFFSET %s"
    params.append(per_page)
    params.append(offset)
    
    cursor.execute(query, tuple(params))
    products = cursor.fetchall()

    # Calcul du total pour la pagination
    count_query = "SELECT COUNT(*) as total FROM Produits WHERE 1=1"
    count_params = []
    if categorie:
        count_query += " AND LOWER(categorie) = LOWER(%s)"
        count_params.append(categorie)
    if search:
        count_query += " AND (nom LIKE %s OR description LIKE %s)"
        count_params.append('%' + search + '%')
        count_params.append('%' + search + '%')
    cursor.execute(count_query, tuple(count_params))
    total = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    return render_template("produits.html", products=products, total=total, page=page, per_page=per_page)


# on récupère le produit sélectionné et les avis liés à ce produit
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
    
    # Utilisation de la fonction SQL CalculerMoyenneNotes pour obtenir la note moyenne
    cursor.execute("SELECT CalculerMoyenneNotes(%s) AS note_moyenne", (produit_id,))
    result = cursor.fetchone()
    if result and result.get("note_moyenne") is not None:
        product["note_moyenne"] = result["note_moyenne"]
    else:
        product["note_moyenne"] = 0

    # Récupération des avis pour ce produit
    cursor.execute("SELECT * FROM Avis WHERE id_produit = %s ORDER BY date_avis DESC", (produit_id,))
    reviews = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("detail-produit.html", product=product, reviews=reviews)


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


if __name__ == "__main__":
    app.run(debug=True)


