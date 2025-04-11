// pour exécuter le code dè le chargement de la page
$(document).ready(function(){
    console.log("produits.js loaded");
  
    // Mise à jour dynamique de l'affichage ddu prix maximum
    $('#price-range').on('input', function() {
      $('#price-value').text($(this).val());
    });
  
    // fonction qui permettra d'appliquer les filtres
    function applyFilters() {
      // On récupère le terme de recherche
      var search = $('#search').val().trim();
      // On récupère le genre (la première case cochée)
      var genre = $("input[name='genre']:checked").first().val();
      // On récupère la première taille cochée
      var taille = $("input[name='taille']:checked").first().val();
      // On récupère le première couleur cochée
      var couleur = $("input[name='couleur']:checked").first().val();
      // On récupère le prix maximum
      var price_max = $('#price-range').val();
       // Récupération du critère de tri depuis le select (c'est la ligne ajoutée)
      var sort_by = $('#sort-by').val();
  
      // Construction des paramètres GET
      var queryParams = {};
      if(search !== "") {
        queryParams.search = search;
      }
      if(genre) {
        queryParams.genre = genre;
      }
      if(price_max) {
        queryParams.price_max = price_max;
      }
      if(taille) {
        queryParams.taille = taille;
      }
      if(couleur) {
        queryParams.couleur = couleur;
      }
      if(sort_by) {
        queryParams.sort_by = sort_by;
      }
      var queryString = $.param(queryParams);
      console.log("Redirecting to: /produits?" + queryString);
      window.location.href = '/produits?' + queryString;
    }

    
    
    // On gère le changement de critère de tri par l'appel de la fonction applyFilters
    $('#sort-by').on('change', function(e) {
        e.preventDefault();
        applyFilters();
    });
  
    // On gère le clic sur  le bouton "Appliquer les filtres" par l'appel de la fonction applyFilters
    $('#apply-filters').on('click', function(e) {
      e.preventDefault();
      applyFilters();
    });
  
    // On gère le clic sur l'icône de recherche par l'appel de la fonction applyFilters
    $('#search-btn').on('click', function(e) {
      e.preventDefault();
      applyFilters();
    });
  
    // On gère le clic sur le Bouton "Réinitialiser" qui nous redirige ensuite vers /produits sans paramètres
    $('#reset-filters').on('click', function(e) {
      e.preventDefault();
      window.location.href = '/produits';
    });
  });
  