$(document).ready(function(){
    // Incrémentation de la quantité
    $(".increase-qty").click(function(){
        var input = $(this).siblings(".item-qty");
        var currentVal = parseInt(input.val());
        var maxVal = parseInt(input.attr('max')) || 10; // valeur max par défaut : 10
        if(currentVal < maxVal) {
            input.val(currentVal + 1);
        }
        updateItemTotal($(this).closest(".cart-item"));
        updateCartSummary();
    });

    // Décrémentation de la quantité
    $(".decrease-qty").click(function(){
        var input = $(this).siblings(".item-qty");
        var currentVal = parseInt(input.val());
        var minVal = parseInt(input.attr('min')) || 1;
        if(currentVal > minVal) {
            input.val(currentVal - 1);
        }
        updateItemTotal($(this).closest(".cart-item"));
        updateCartSummary();
    });

    // Vider le panier
    $("#clear-cart").click(function(){
        if(confirm("Voulez-vous vraiment vider le panier ?")){
            $.ajax({
                url: "/vider-panier",
                type: "POST",
                success: function(response){
                    if(response.success){
                        location.reload();
                    }
                },
                error: function(){
                    alert("Une erreur est survenue lors du vidage du panier.");
                }
            });
        }
    });

    // Mettre à jour le panier
    $("#update-cart").click(function(){
        var cart_updates = [];
        $(".cart-item").each(function(){
            var product_id = $(this).data("product-id");
            var quantity = $(this).find(".item-qty").val();
            cart_updates.push({
                product_id: product_id,
                quantity: quantity
            });
        });
        $.ajax({
            url: "/update-panier",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({cart_updates: cart_updates}),
            success: function(response){
                if(response.success){
                    alert("Panier mis à jour !");
                    location.reload(); // ou bien mettre à jour le DOM localement
                }
            },
            error: function(){
                alert("Une erreur est survenue lors de la mise à jour du panier.");
            }
        });
    });

    // Supprimer un article individuel
    $(".remove-item").click(function(){
        if(confirm("Voulez-vous supprimer cet article du panier ?")){
            var cartItem = $(this).closest(".cart-item");
            var product_id = cartItem.data("product-id");
            $.ajax({
                url: "/remove-item",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({product_id: product_id}),
                success: function(response){
                    if(response.success){
                        location.reload();
                    }
                },
                error: function(){
                    alert("Une erreur est survenue lors de la suppression de l'article.");
                }
            });
        }
    });
});

// Fonction pour mettre à jour le total de la ligne d’un article
function updateItemTotal(cartItem){
    var quantity = parseInt(cartItem.find(".item-qty").val());
    // On suppose que le prix est affiché dans le span qui contient "$" suivi du prix
    var priceText = cartItem.find("span.text-nowrap").first().text();
    var price = parseFloat(priceText.replace("$",""));
    var total = quantity * price;
    cartItem.find(".item-total").text("$" + total.toFixed(2));
}

// Fonction pour recalculer le récapitulatif du panier
function updateCartSummary(){
    var subtotal = 0;
    $(".cart-item").each(function(){
        var quantity = parseInt($(this).find(".item-qty").val());
        var priceText = $(this).find("span.text-nowrap").first().text();
        var price = parseFloat(priceText.replace("$",""));
        subtotal += quantity * price;
    });
    $("#subtotal").text("$" + subtotal.toFixed(2));
    var shipping_cost = (subtotal > 0 ? 4.99 : 0);
    $("#shipping-cost").text("$" + shipping_cost.toFixed(2));
    var tax = subtotal * 0.20;
    $("#tax-amount").text("$" + tax.toFixed(2));
    var total = subtotal + shipping_cost + tax;
    $("#total-amount").text("$" + total.toFixed(2));
}