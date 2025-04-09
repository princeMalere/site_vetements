from flask import Flask, render_template, request
import pymysql, pymysql.cursors

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Remplacez par une clé secrète forte

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Mr_Robot_272000',  # Remplacez par votre mot de passe
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

# -----------------------
# Vous pouvez ajouter d'autres routes (ex. : détails d'un produit) au fur et à mesure.
# -----------------------

if __name__ == "__main__":
    app.run(debug=True)


