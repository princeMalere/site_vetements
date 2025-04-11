document.querySelectorAll('input[name="shipping-method"]').forEach(function(radio) {
    radio.addEventListener('change', function() {
        // Supposons que vous avez des fonctions en JS pour récupérer le sous-total et recalculer
        var subtotal = parseFloat(document.getElementById('subtotal').textContent.replace('$',''));
        var shippingCost = 0.0;
        if (this.value === 'express') {
            shippingCost = 9.99;
        } else if (this.value === 'pickup') {
            shippingCost = 0.0;
        } else {
            shippingCost = 4.99;
        }
        var tax = subtotal * 0.20;
        var total = subtotal + shippingCost + tax;
        document.getElementById('shipping-cost').textContent = "$" + shippingCost.toFixed(2);
        document.getElementById('tax-amount').textContent = "$" + tax.toFixed(2);
        document.getElementById('total-amount').textContent = "$" + total.toFixed(2);
    });
});

document.addEventListener('DOMContentLoaded', function(){
    const shippingForm = document.getElementById('shipping-form');

    shippingForm.addEventListener('submit', function(e) {
        // On part du principe que le formulaire est valide
        let formIsValid = true;

        // On sélectionne tous les champs ayant l'attribut 'required'
        const requiredFields = shippingForm.querySelectorAll('[required]');
        
        // Parcours de chaque champ requis
        requiredFields.forEach(function(field) {
            // Effacer les erreurs précédentes
            field.classList.remove('is-invalid');
            let feedback = field.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = '';
                feedback.style.display = 'none';
            }

            // Vérifier si le champ est vide
            if (!field.value.trim()) {
                formIsValid = false;
                field.classList.add('is-invalid');
                // Récupérer un message personnalisé s'il est défini, sinon utiliser un message par défaut
                let errorMessage = field.getAttribute('data-error') || "Ce champ est obligatoire.";
                
                // Vérifier s'il y a déjà un élément pour le message d'erreur
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    field.parentNode.insertBefore(feedback, field.nextSibling);
                }
                feedback.textContent = errorMessage;
                feedback.style.display = 'block';
            }
        });
        
        // Si le formulaire n'est pas valide, on empêche sa soumission
        if (!formIsValid) {
            e.preventDefault();
            // Optionnel : faire défiler l'écran jusqu'au premier champ invalide
            const firstError = shippingForm.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });
});

