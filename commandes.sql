DROP DATABASE IF EXISTS ecommerce_db;
CREATE DATABASE ecommerce_db;
USE ecommerce_db;

CREATE TABLE Utilisateurs (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mdp VARCHAR(255) NOT NULL,
    type ENUM('Admin', 'Client') NOT NULL,
    date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Clients (
    id_user INT PRIMARY KEY,
    adresse VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_user) REFERENCES Utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE Admins (
    id_user INT PRIMARY KEY,
    FOREIGN KEY (id_user) REFERENCES Utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE Produits (
    id_produit INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    prix DECIMAL(10,2) NOT NULL CHECK (prix > 0),
    stock INT NOT NULL CHECK (stock >= 0),
    categorie VARCHAR(50) NOT NULL,
    taille VARCHAR(10) NOT NULL, -- XS, S, M, L, XL, XXL
    couleur VARCHAR(30) NOT NULL,
    matiere VARCHAR(50) NOT NULL,
    genre ENUM('Homme', 'Femme', 'Unisexe') NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    note_moyenne DECIMAL(5,2) DEFAULT 0,
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Paniers (
    id_panier INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    statut ENUM('actif', 'validé', 'annulé') NOT NULL DEFAULT 'actif',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES Utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE Commandes (
    id_commande INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    id_panier INT NOT NULL,
    date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut ENUM('en attente', 'expédiée', 'livrée', 'annulée') NOT NULL DEFAULT 'en attente',
    FOREIGN KEY (id_user) REFERENCES Utilisateurs(id_user),
    FOREIGN KEY (id_panier) REFERENCES Paniers(id_panier),
    UNIQUE KEY (id_panier)
);

CREATE TABLE Panier_Produits (
    id_panier INT NOT NULL,
    id_produit INT NOT NULL,
    quantite INT NOT NULL CHECK (quantite > 0),
    PRIMARY KEY (id_panier, id_produit),
    FOREIGN KEY (id_panier) REFERENCES Paniers(id_panier) ON DELETE CASCADE,
    FOREIGN KEY (id_produit) REFERENCES Produits(id_produit)
);

CREATE TABLE Paiements (
    id_paiement INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL,
    montant DECIMAL(10,2) NOT NULL CHECK (montant > 0),
    methode ENUM('carte', 'paypal') NOT NULL,
    statut ENUM('en attente', 'réussi', 'échec') NOT NULL DEFAULT 'en attente',
    date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_commande) REFERENCES Commandes(id_commande)
);

CREATE TABLE Avis (
    id_avis INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    id_produit INT NOT NULL,
    note INT NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire VARCHAR(255),
    date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES Utilisateurs(id_user),
    FOREIGN KEY (id_produit) REFERENCES Produits(id_produit),
    UNIQUE KEY (id_user, id_produit)
);

CREATE TABLE Historique_Commandes (
    id_historique INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL,
    ancien_statut ENUM('en attente', 'expédiée', 'livrée', 'annulée'),
    nouveau_statut ENUM('en attente', 'expédiée', 'livrée', 'annulée'),
    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_commande) REFERENCES Commandes(id_commande)
);

-- Création de la table Livraisons pour stocker les informations de livraison des commandes
CREATE TABLE Livraisons (
    id_livraison INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL, -- Référence à la commande
    adresse VARCHAR(255) NOT NULL,
    complement VARCHAR(255),
    code_postal VARCHAR(20) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    pays VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    mode_livraison ENUM('standard', 'express', 'pickup') DEFAULT 'standard',
    date_livraison_prevue DATE,
    date_livraison_effective DATE,
    CONSTRAINT fk_commande_livraison FOREIGN KEY (id_commande) REFERENCES Commandes(id_commande)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


---------------------------------------------------------------------
-- Peuplement de la base de données
---------------------------------------------------------------------
-- Insertion des utilisateurs - Utilisation de BCrypt pour le hachage des mots de passe
-- Note: En production, utilisez la fonction de hachage de votre framework

-- Insertion des utilisateurs de type admin
INSERT INTO Utilisateurs (nom, prenom, email, mdp, type) VALUES
('Dubois', 'Jean', 'jean.dubois@example.com', '$2y$10$hashed1', 'Admin'),
('Lefebvre', 'Marie', 'marie.lefebvre@example.com', '$2y$10$hashed2', 'Admin'),
('Martin', 'Lucas', 'lucas.martin@example.com', '$2y$10$hashed3', 'Admin');

-- Insertion des administrateurs
INSERT INTO Admins (id_user) VALUES 
(1), (2), (3);

-- Insertion des utilisateurs de type client
INSERT INTO Utilisateurs (nom, prenom, email, mdp, type) VALUES
('Bernard', 'Sophie', 'sophie.bernard@example.com', '$2y$10$hashed4', 'Client'),
('Petit', 'Thomas', 'thomas.petit@example.com', '$2y$10$hashed5', 'Client'),
('Robert', 'Emma', 'emma.robert@example.com', '$2y$10$hashed6', 'Client'),
('Richard', 'Louis', 'louis.richard@example.com', '$2y$10$hashed7', 'Client'),
('Moreau', 'Camille', 'camille.moreau@example.com', '$2y$10$hashed8', 'Client'),
('Simon', 'Léa', 'lea.simon@example.com', '$2y$10$hashed9', 'Client'),
('Laurent', 'Hugo', 'hugo.laurent@example.com', '$2y$10$hashed10', 'Client'),
('Michel', 'Chloé', 'chloe.michel@example.com', '$2y$10$hashed11', 'Client'),
('Leroy', 'Nathan', 'nathan.leroy@example.com', '$2y$10$hashed12', 'Client'),
('Garcia', 'Sarah', 'sarah.garcia@example.com', '$2y$10$hashed13', 'Client'),
('Fournier', 'Maxime', 'maxime.fournier@example.com', '$2y$10$hashed14', 'Client'),
('Mercier', 'Laura', 'laura.mercier@example.com', '$2y$10$hashed15', 'Client'),
('Dupont', 'Alexandre', 'alexandre.dupont@example.com', '$2y$10$hashed16', 'Client');

-- Insertion des adresses clients
INSERT INTO Clients (id_user, adresse) VALUES 
(4, '15 rue de la Paix, 75001 Paris'),
(5, '8 avenue des Champs-Élysées, 75008 Paris'),
(6, '12 boulevard Saint-Michel, 75005 Paris'),
(7, '23 rue du Faubourg Saint-Honoré, 75008 Paris'),
(8, '5 place de la Bastille, 75004 Paris'),
(9, '19 rue de Rivoli, 75001 Paris'),
(10, '7 rue Mouffetard, 75005 Paris'),
(11, '14 rue de la Pompe, 75016 Paris'),
(12, '3 avenue Montaigne, 75008 Paris'),
(13, '27 rue Saint-Antoine, 75004 Paris'),
(14, '10 rue de Vaugirard, 75006 Paris'),
(15, '2 place de la Concorde, 75001 Paris'),
(16, '16 rue des Martyrs, 75009 Paris');

-- Insertion des catégories de produits
INSERT INTO Produits (nom, description, prix, stock, categorie, taille, couleur, matiere, genre, image_url) VALUES
-- Hauts pour hommes
('Chemise Oxford', 'Chemise en coton Oxford avec coupe slim fit et col boutonné', 49.99, 120, 'Chemises', 'M', 'Bleu ciel', 'Coton Oxford', 'Homme', '/images/products/oxford_shirt_blue.jpg'),
('Polo classique', 'Polo confortable en maille piquée de coton', 39.99, 85, 'Polos', 'L', 'Noir', 'Coton piqué', 'Homme', '/images/products/classic_polo_black.jpg'),
('T-shirt basique', 'T-shirt col rond en coton doux et respirant', 19.99, 200, 'T-shirts', 'M', 'Blanc', 'Coton bio', 'Homme', '/images/products/basic_tshirt_white.jpg'),
('Pull col roulé', 'Pull chaud en laine mérinos à col roulé', 69.99, 60, 'Pulls', 'XL', 'Gris anthracite', 'Laine mérinos', 'Homme', '/images/products/turtleneck_grey.jpg'),
('Sweat à capuche', 'Sweatshirt à capuche avec poche kangourou', 59.99, 75, 'Sweats', 'L', 'Marine', 'Coton molletonné', 'Homme', '/images/products/hoodie_navy.jpg'),

-- Hauts pour femmes
('Blouse bohème', 'Blouse légère aux détails brodés et manches amples', 45.99, 70, 'Blouses', 'S', 'Écru', 'Viscose', 'Femme', '/images/products/boho_blouse.jpg'),
('T-shirt col V', 'T-shirt basique col V en coton stretch', 24.99, 150, 'T-shirts', 'M', 'Rouge', 'Coton stretch', 'Femme', '/images/products/vneck_tshirt_red.jpg'),
('Chemisier satiné', 'Chemisier élégant en tissu satiné avec col lavallière', 59.99, 55, 'Chemisiers', 'S', 'Emeraude', 'Satin polyester', 'Femme', '/images/products/satin_blouse_emerald.jpg'),
('Pull oversize', 'Pull ample et confortable à col bateau', 64.99, 60, 'Pulls', 'M', 'Beige', 'Laine mélangée', 'Femme', '/images/products/oversized_sweater_beige.jpg'),
('Top à bretelles', 'Top léger à bretelles fines ajustables', 29.99, 90, 'Tops', 'XS', 'Noir', 'Viscose', 'Femme', '/images/products/cami_top_black.jpg'),

-- Bas pour hommes
('Jean slim', 'Jean coupe slim en denim robuste et légèrement élastique', 69.99, 110, 'Jeans', '42', 'Bleu foncé', 'Denim stretch', 'Homme', '/images/products/slim_jeans.jpg'),
('Pantalon chino', 'Pantalon chino classique en coton', 59.99, 85, 'Pantalons', '44', 'Beige', 'Coton', 'Homme', '/images/products/chino_pants_beige.jpg'),
('Short en jean', 'Short en denim avec ourlets retroussés', 39.99, 70, 'Shorts', '40', 'Bleu délavé', 'Denim', 'Homme', '/images/products/denim_shorts.jpg'),
('Pantalon de jogging', 'Pantalon de jogging confortable avec taille élastique', 49.99, 90, 'Joggings', 'L', 'Gris', 'Coton molletonné', 'Homme', '/images/products/joggers_grey.jpg'),
('Bermuda cargo', 'Bermuda style cargo avec multiples poches', 44.99, 65, 'Shorts', '42', 'Kaki', 'Coton', 'Homme', '/images/products/cargo_shorts_khaki.jpg'),

-- Bas pour femmes
('Jean skinny taille haute', 'Jean skinny taille haute avec effet sculptant', 69.99, 120, 'Jeans', '38', 'Noir', 'Denim super stretch', 'Femme', '/images/products/high_waist_skinny_black.jpg'),
('Jupe plissée midi', 'Jupe midi plissée élégante', 54.99, 60, 'Jupes', 'S', 'Rouge bordeaux', 'Polyester', 'Femme', '/images/products/pleated_skirt_burgundy.jpg'),
('Pantalon palazzo', 'Pantalon large style palazzo fluide et élégant', 65.99, 50, 'Pantalons', 'M', 'Bleu marine', 'Crêpe', 'Femme', '/images/products/palazzo_pants_navy.jpg'),
('Legging fitness', 'Legging de sport taille haute avec poche latérale', 34.99, 100, 'Leggings', 'S', 'Noir', 'Polyamide Elasthanne', 'Femme', '/images/products/fitness_leggings_black.jpg'),
('Short en lin', 'Short décontracté en lin avec taille élastique', 39.99, 70, 'Shorts', 'M', 'Blanc', 'Lin', 'Femme', '/images/products/linen_shorts_white.jpg'),

-- Vestes et manteaux
('Veste en jean', 'Veste en jean classique légèrement délavée', 79.99, 65, 'Vestes', 'L', 'Bleu moyen', 'Denim', 'Unisexe', '/images/products/denim_jacket.jpg'),
('Blouson bomber', 'Blouson style bomber avec finitions côtelées', 89.99, 55, 'Vestes', 'M', 'Vert olive', 'Polyester', 'Homme', '/images/products/bomber_jacket_olive.jpg'),
('Trench coat', 'Trench coat classique ceinturé imperméable', 129.99, 40, 'Manteaux', 'M', 'Beige', 'Coton enduit', 'Femme', '/images/products/trenchcoat_beige.jpg'),
('Veste en cuir', 'Veste motard en cuir véritable avec détails zippés', 199.99, 30, 'Vestes', 'L', 'Noir', 'Cuir', 'Unisexe', '/images/products/leather_jacket_black.jpg'),
('Doudoune légère', 'Doudoune légère compressible et chaude', 109.99, 75, 'Manteaux', 'M', 'Bleu marine', 'Nylon et duvet', 'Unisexe', '/images/products/light_puffer_navy.jpg');

-- Création de paniers
INSERT INTO Paniers (id_user, statut, date_creation) VALUES
-- Paniers actifs
(4, 'actif', '2025-03-25 10:32:15'),
(5, 'actif', '2025-03-26 14:45:20'),
(8, 'actif', '2025-03-28 09:12:37'),
(10, 'actif', '2025-03-29 16:30:22'),
(13, 'actif', '2025-03-30 11:24:53'),
-- Paniers validés
(6, 'validé', '2025-03-15 13:45:10'),
(7, 'validé', '2025-03-17 10:24:38'),
(9, 'validé', '2025-03-19 15:17:52'),
(11, 'validé', '2025-03-21 12:36:45'),
(12, 'validé', '2025-03-23 09:51:14'),
(14, 'validé', '2025-03-24 14:05:37'),
(15, 'validé', '2025-03-25 17:39:22'),
(16, 'validé', '2025-03-26 11:28:33'),
-- Paniers annulés
(5, 'annulé', '2025-03-10 09:12:45'),
(8, 'annulé', '2025-03-12 16:43:28');

-- Ajout de produits aux paniers
INSERT INTO Panier_Produits (id_panier, id_produit, quantite) VALUES
-- Panier 1 (actif)
(1, 1, 1),  -- Chemise Oxford
(1, 5, 1),  -- Sweat à capuche
-- Panier 2 (actif)
(2, 11, 2),  -- Jean slim
(2, 24, 1),  -- Veste en cuir
-- Panier 3 (actif)
(3, 6, 1),   -- Blouse bohème
(3, 9, 2),   -- Pull oversize
-- Panier 4 (actif)
(4, 3, 2),   -- T-shirt basique
(4, 14, 1),  -- Pantalon de jogging
-- Panier 5 (actif)
(5, 16, 1),  -- Jupe plissée midi
(5, 8, 1),   -- Chemisier satiné
-- Panier 6 (validé)
(6, 2, 1),   -- Polo classique
(6, 13, 1),  -- Short en jean
-- Panier 7 (validé)
(7, 7, 1),   -- T-shirt col V
(7, 15, 2),  -- Jean skinny taille haute
-- Panier 8 (validé)
(8, 12, 1),  -- Pantalon chino
(8, 4, 1),   -- Pull col roulé
-- Panier 9 (validé)
(9, 10, 1),  -- Top à bretelles
(9, 18, 2),  -- Legging fitness
-- Panier 10 (validé)
(10, 21, 1), -- Blouson bomber
(10, 25, 1), -- Doudoune légère
-- Panier 11 (validé)
(11, 19, 1), -- Short en lin
(11, 23, 1), -- Trench coat
-- Panier 12 (validé)
(12, 1, 2),  -- Chemise Oxford
(12, 20, 1), -- Veste en jean
-- Panier 13 (validé)
(13, 17, 1), -- Pantalon palazzo
(13, 22, 1); -- Veste en cuir

-- Création de commandes pour les paniers validés
INSERT INTO Commandes (id_user, id_panier, date_commande, statut) VALUES
(6, 6, '2025-03-15 13:46:10', 'livrée'),       -- Commande ancienne, déjà livrée
(7, 7, '2025-03-17 10:25:38', 'livrée'),       -- Commande ancienne, déjà livrée
(9, 8, '2025-03-19 15:18:52', 'expédiée'),      -- Commande en cours de livraison
(11, 9, '2025-03-21 12:37:45', 'expédiée'),     -- Commande en cours de livraison
(12, 10, '2025-03-23 09:52:14', 'en attente'),  -- Commande récente
(14, 11, '2025-03-24 14:06:37', 'en attente'),  -- Commande récente
(15, 12, '2025-03-25 17:40:22', 'en attente'),  -- Commande très récente
(16, 13, '2025-03-26 11:29:33', 'annulée');     -- Commande annulée

-- Création des paiements
INSERT INTO Paiements (id_commande, montant, methode, statut, date_paiement) VALUES
(1, 1449.98, 'carte', 'réussi', '2025-03-15 13:46:30'),
(2, 199.97, 'paypal', 'réussi', '2025-03-17 10:26:15'),
(3, 429.98, 'carte', 'réussi', '2025-03-19 15:19:32'),
(4, 88.96, 'paypal', 'réussi', '2025-03-21 12:38:20'),
(5, 219.97, 'carte', 'réussi', '2025-03-23 09:53:05'),
(6, 354.98, 'carte', 'en attente', '2025-03-24 14:07:18'),
(7, 119.97, 'paypal', 'en attente', '2025-03-25 17:41:05'),
(8, 899.98, 'carte', 'échec', '2025-03-26 11:30:15');

-- Ajout d'avis sur les produits
INSERT INTO Avis (id_user, id_produit, note, commentaire, date_avis) VALUES
-- Avis sur les chemises et polos
(4, 1, 5, 'Excellente chemise, coupe parfaite et tissu de qualité !', '2025-03-10 14:32:45'),
(6, 1, 4, 'Bonne chemise mais les manches sont un peu courtes pour moi.', '2025-03-12 10:25:36'),
(7, 2, 5, 'Ce polo est idéal pour le travail, confortable toute la journée.', '2025-03-15 17:43:21'),
(9, 2, 4, 'Bon rapport qualité-prix, la couleur est un peu plus claire que sur la photo.', '2025-03-18 09:15:47'),
-- Avis sur les t-shirts
(11, 3, 5, 'T-shirt basique parfait, je l\'ai acheté en plusieurs couleurs !', '2025-03-20 12:36:58'),
(13, 3, 4, 'Bon t-shirt, mais prendre une taille au-dessus car il rétrécit au lavage.', '2025-03-22 15:27:19'),
(5, 7, 4, 'J\'adore ce t-shirt col V, la coupe est très flatteuse.', '2025-03-14 11:52:33'),
-- Avis sur les pulls et sweats
(8, 9, 5, 'Ce pull oversize est ultra confortable et chaud, parfait pour l\'hiver.', '2025-03-16 16:45:28'),
(10, 4, 4, 'Très beau pull, le col roulé tient bien sa forme même après plusieurs lavages.', '2025-03-19 13:21:47'),
(12, 5, 5, 'Ce sweat à capuche est devenu mon indispensable, doublure très douce !', '2025-03-21 10:33:15'),
-- Avis sur les jeans et pantalons
(14, 11, 5, 'Jean slim parfait, bon maintien et ne se déforme pas.', '2025-03-24 18:17:42'),
(15, 12, 4, 'Chino très élégant, taille un peu grande prévoir une taille en dessous.', '2025-03-25 14:29:36'),
(16, 15, 5, 'Jean skinny super confortable grâce au stretch, taille haute parfaite !', '2025-03-23 09:45:28'),
(7, 17, 4, 'Pantalon palazzo élégant pour le bureau, tissu un peu fin.', '2025-03-26 17:53:14'),
-- Avis sur les vestes et manteaux
(8, 21, 5, 'Blouson bomber super stylé et chaud, je le porte tous les jours !', '2025-03-17 09:42:15'),
(9, 22, 4, 'Bon trench, imperméable comme promis, manque juste une doublure amovible.', '2025-03-18 16:33:29'),
(10, 24, 5, 'Cette veste en cuir est un investissement, qualité exceptionnelle !', '2025-03-19 12:15:48'),
(11, 25, 4, 'Doudoune très légère et chaude, parfaite pour les voyages.', '2025-03-20 14:27:36');

---------------------------------------------------------------------
-- Création des requêtes et des routines
---------------------------------------------------------------------
-- Requêtes avancées

-- Requête retournant la note moyenne et le nombre d'avis utilisateurs pour chaque produit
SELECT 
    p.id_produit,
    p.nom,
    AVG(a.note) AS note_moyenne,
    COUNT(a.id_avis) AS nombre_avis
FROM Produits p
LEFT JOIN Avis a ON p.id_produit = a.id_produit
GROUP BY p.id_produit;

-- Requête permettant de récupérer les noms des clients n'ayant effectué aucune commande
SELECT u.nom, u.prenom
FROM Utilisateurs u
JOIN Clients c ON u.id_user = c.id_user
LEFT JOIN Commandes cm ON u.id_user = cm.id_user
WHERE cm.id_commande IS NULL;

-- Requête affichant chaque commande avec ses détails
SELECT 
    cm.id_commande,
    cm.date_commande,
    u.nom AS client_nom,
    u.prenom AS client_prenom,
    cm.statut AS commande_statut,
    p.nom AS produit_nom,
    pp.quantite,
    p.prix
FROM Commandes cm
JOIN Utilisateurs u ON cm.id_user = u.id_user
JOIN Panier_Produits pp ON cm.id_panier = pp.id_panier
JOIN Produits p ON pp.id_produit = p.id_produit
ORDER BY cm.id_commande;

---------------------------------------------------------------------
-- Procédures et fonctions
---------------------------------------------------------------------
-- Procédure pour la conversion d'un panier en commande
DELIMITER //
CREATE PROCEDURE ConvertirPanierEnCommande(IN p_id_panier INT)
BEGIN
    DECLARE v_id_user INT;
    DECLARE v_id_commande INT;

    -- Récupérer l'ID de l'utilisateur lié au panier
    SELECT id_user INTO v_id_user
    FROM Paniers
    WHERE id_panier = p_id_panier;

    -- Créer une nouvelle commande pour ce panier
    INSERT INTO Commandes (id_user, id_panier, date_commande, statut)
    VALUES (v_id_user, p_id_panier, NOW(), 'en attente');
    SET v_id_commande = LAST_INSERT_ID();

    -- Mettre à jour le statut du panier pour indiquer qu'il a été validé
    UPDATE Paniers
    SET statut = 'validé'
    WHERE id_panier = p_id_panier;

    -- Insérer un enregistrement dans la table Livraisons avec des valeurs par défaut
    INSERT INTO Livraisons (id_commande, adresse, code_postal, ville, pays, telephone, mode_livraison)
    VALUES (v_id_commande, '', '', '', '', '', 'standard');
END //
DELIMITER ;


-- Procédure pour annuler une commande
DELIMITER //
CREATE PROCEDURE AnnulerCommande(IN p_id_commande INT)
BEGIN
    -- Mettre à jour le statut de la commande à 'annulée'
    UPDATE Commandes
    SET statut = 'annulée'
    WHERE id_commande = p_id_commande;

    -- (Optionnel) Mettre à jour le statut du panier associé
    UPDATE Paniers
    SET statut = 'annulé'
    WHERE id_panier = (SELECT id_panier FROM Commandes WHERE id_commande = p_id_commande);
END //
DELIMITER ;

-- Procédure de mise à jour du statut de la commande et enregistrement dans l'historique
DELIMITER //
CREATE PROCEDURE MettreAJourStatutCommande(
    IN p_id_commande INT,
    IN p_nouveau_statut VARCHAR(20)
)
BEGIN
    DECLARE v_ancien_statut VARCHAR(20);

    -- Récupérer le statut actuel de la commande
    SELECT statut INTO v_ancien_statut
    FROM Commandes
    WHERE id_commande = p_id_commande;

    -- Mettre à jour le statut de la commande
    UPDATE Commandes
    SET statut = p_nouveau_statut
    WHERE id_commande = p_id_commande;

    -- Enregistrer le changement dans l'historique
    INSERT INTO Historique_Commandes (id_commande, ancien_statut, nouveau_statut, date_modification)
    VALUES (p_id_commande, v_ancien_statut, p_nouveau_statut, NOW());
END //
DELIMITER ;

-- Fonction pour le calcul de la moyenne des notes d'un produit
DELIMITER //
CREATE FUNCTION CalculerMoyenneNotes(p_id_produit INT) RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    DECLARE moyenne DECIMAL(5,2);

    SELECT AVG(note) INTO moyenne
    FROM Avis
    WHERE id_produit = p_id_produit;

    RETURN IFNULL(moyenne, 0);
END //
DELIMITER ;

-- Fonction retournant le montant total d'un panier
DELIMITER //
CREATE FUNCTION CalculerMontantTotalPanier(p_id_panier INT) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);

    SELECT SUM(pp.quantite * p.prix) INTO total
    FROM Panier_Produits pp
    JOIN Produits p ON pp.id_produit = p.id_produit
    WHERE pp.id_panier = p_id_panier;

    RETURN IFNULL(total, 0);
END //
DELIMITER ;

-- Procédure pour la suppression d'un panier inactif depuis un certain temps
DELIMITER //
CREATE PROCEDURE SupprimerPanierInactif(IN p_delai INT)
BEGIN
    DELETE FROM Paniers
    WHERE statut = 'actif'
      AND date_creation < DATE_SUB(NOW(), INTERVAL p_delai DAY);
END //
DELIMITER ;

---------------------------------------------------------------------
-- Triggers
---------------------------------------------------------------------
-- Trigger permettant de décrémenter le stock d'un produit dès qu'un article est ajouté à une commande
DELIMITER //
CREATE TRIGGER decremente_stock_apres_ajout_commande
AFTER INSERT ON Panier_Produits
FOR EACH ROW
BEGIN
    UPDATE Produits
    SET stock = stock - NEW.quantite
    WHERE id_produit = NEW.id_produit;
END //
DELIMITER ;

-- Trigger empêchant l'ajout d'un produit dont le stock est insuffisant
DELIMITER //
CREATE TRIGGER verif_stock_avant_ajout_commande
BEFORE INSERT ON Panier_Produits
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;
    
    SELECT stock INTO v_stock
    FROM Produits
    WHERE id_produit = NEW.id_produit;
    
    IF v_stock < NEW.quantite THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Stock insuffisant pour ce produit';
    END IF;
END //
DELIMITER ;

-- Trigger pour la mise à jour de la note moyenne d'un produit après insertion d'un avis
DELIMITER //
CREATE TRIGGER update_note_moyenne_apres_insertion_avis
AFTER INSERT ON Avis
FOR EACH ROW
BEGIN
    DECLARE v_moyenne DECIMAL(5,2);
    
    SELECT AVG(note) INTO v_moyenne
    FROM Avis
    WHERE id_produit = NEW.id_produit;
    
    UPDATE Produits
    SET note_moyenne = IFNULL(v_moyenne, 0)
    WHERE id_produit = NEW.id_produit;
END //
DELIMITER ;

-- Trigger pour la mise à jour de la note moyenne d'un produit après mise à jour d'un avis
DELIMITER //
CREATE TRIGGER update_note_moyenne_apres_update_avis
AFTER UPDATE ON Avis
FOR EACH ROW
BEGIN
    DECLARE v_moyenne DECIMAL(5,2);
    
    SELECT AVG(note) INTO v_moyenne
    FROM Avis
    WHERE id_produit = NEW.id_produit;
    
    UPDATE Produits
    SET note_moyenne = IFNULL(v_moyenne, 0)
    WHERE id_produit = NEW.id_produit;
END //
DELIMITER ;

-- Trigger pour la mise à jour de la note moyenne d'un produit après suppression d'un avis
DELIMITER //
CREATE TRIGGER update_note_moyenne_apres_delete_avis
AFTER DELETE ON Avis
FOR EACH ROW
BEGIN
    DECLARE v_moyenne DECIMAL(5,2);
    
    SELECT AVG(note) INTO v_moyenne
    FROM Avis
    WHERE id_produit = OLD.id_produit;
    
    UPDATE Produits
    SET note_moyenne = IFNULL(v_moyenne, 0)
    WHERE id_produit = OLD.id_produit;
END //
DELIMITER ;

-- trigger responsable d'insérer une ligne dans Historique_Commandes avec l'ancien et le nouveau statut et la date de modification
DELIMITER //
CREATE TRIGGER historique_commandes_after_update
AFTER UPDATE ON Commandes
FOR EACH ROW
BEGIN
    IF OLD.statut <> NEW.statut THEN
        INSERT INTO Historique_Commandes (id_commande, ancien_statut, nouveau_statut, date_modification)
        VALUES (NEW.id_commande, OLD.statut, NEW.statut, NOW());
    END IF;
END //
DELIMITER ;

