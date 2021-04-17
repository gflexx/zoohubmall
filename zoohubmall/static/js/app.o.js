$(document).foundation()
$(document).ready(function(){

	// fadeout notification
	var callOut = $('.success_callout');
	callOut.fadeOut(3600, 'swing');
	
	// separate thousands with commas
	function toCommas(value) {
		return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}
	
	// Snackbar
	function showSnackBar(message){
		var snack = document.getElementById("snackbar");
		var snackText = $('.snacktext');
		snackText.text(message);
		snack.className = "show";
		setTimeout(function(){
			snack.className = snack.className.replace("show", "");
		}, 2700);
	}
	
	// add review ajax
	var addReviewForm = $(".review-form");
	addReviewForm.submit(function reviewAjax(event){
		event.preventDefault();
		var thisForm = $(this);
		var formAction = thisForm.attr('action');
		var formMethod = thisForm.attr('method');
		var formData = thisForm.serialize();
		$.ajax({
			url: formAction,
			method: formMethod,
			data: formData,
			dataType: 'json',
			success: function(data){
				var numReviews = data.numReviews;
				var pluralise = "";
				// pluralize review
				if(numReviews == 1){
					pluralise = "Review";
				}else{
					pluralise = "Reviews";
				}
				$('.reviews-count').text(numReviews);
				$('.reviews-count-pluralize').text(pluralise);
				$('#id_text').val('');
				showSnackBar(data.messageLoad);
				$('.reviews').html(data.reviews);
			},
			error: function(errorData){
				showSnackBar('Oops, something went wrong. Try a refresh');
			}
		})	
	})
	
	// add comment ajax
	var addCommentForm = $(".comment-form");
	addCommentForm.submit(function commentAjax(event){
		event.preventDefault();
		var thisForm = $(this);
		var formAction = thisForm.attr('action');
		var formMethod = thisForm.attr('method');
		var formData = thisForm.serialize();
		$.ajax({
			url: formAction,
			method: formMethod,
			data: formData,
			dataType: 'json',
			success: function(data){
				var numComments = data.numComments;
				var pluralise = "";
				// pluralize comment
				if(numComments == 1){
					pluralise = "Comment";
				}else{
					pluralise = "Comments";
				}
				$('.comment-count').text(numComments);
				$('.comment-count-pluralize').text(pluralise);
				$('#id_text').val('');
				showSnackBar(data.messageLoad);
				$('.comments').html(data.comments);
			},
			error: function(errorData){
				showSnackBar('Oops, something went wrong. Try a refresh');
			}
		})	
	})

	// add to bag ajax
	var addToBagForm = $('.add-to-bag-form');
	addToBagForm.submit(function(event){
		event.preventDefault();
		var thisForm = $(this);
		var formButton = thisForm.find('[type="submit"]');
		var formAction = thisForm.attr('action');
		var formMethod = thisForm.attr('method');
		var formData = thisForm.serialize();
		$.ajax({
			url: formAction,
			method: formMethod,
			data: formData,
			success: function(data){			
				formButton.addClass('secondary');
				var productCount =  $('.num-products-count');
				productCount.text(data.numProducts);
				showSnackBar(data.messageLoad);
                var currentPath = window.location.href;
                if (currentPath.indexOf('bag') != -1){
                    updateBag();
                }
			},
			error: function(errorData){
				showSnackBar('Oops, Something went wrong.');
			}
		})
	})

	// remove from bag ajax
	var removeFromBagForm = $('.remove-from-bag-form');
	removeFromBagForm.submit(function(event){
		event.preventDefault();
		var thisForm = $(this);
		var formAction = thisForm.attr('action');
		var formMethod = thisForm.attr('method');
		var formData = thisForm.serialize();
		$.ajax({
			url: formAction,
			method: formMethod,
			data: formData,
			success: function(data){
				var productCount =  $('.num-products-count');
				productCount.text(data.numProducts);
				$('#' + data.productSlug).remove();
				$('#' + data.productSlug + '-md-sm').remove();
				showSnackBar(data.messageLoad);
                var currentPath = window.location.href;
                if (currentPath.indexOf('bag') != -1){
                    updateBag();
                }
			},
			error: function(errorData){
				showSnackBar('Oops, something went wrong.');
			}
		})
	})

	
	// Increment bag value
	$('.plus-button').click(function() {
		var $input = $(this).parents('.input-group').find('.input-group-field');
		var $maxAmount = $(this).parents('.input-group').find('.max-amount');
		var val = parseInt($input.val());
		var maximum = parseInt($maxAmount.val());
		var $updateForm = $(this).parents('.update-bag-quantity-form');
		var formAction = $updateForm.attr('action');
		var formMethod = $updateForm.attr('method');
		var itemPrice = $(this).parents('.bag-item').find('.item-total');
		
		if (val < maximum){
			$input.val(val + 1);
			var formData = $updateForm.serialize();	
			$.ajax({
				url: formAction,
				method: formMethod,
				data: formData,
				success: function(data){
					showSnackBar(data.messageLoad);
					var itemPriceTotal = data.totalItemPrice;
					lc_itemPrice = toCommas(itemPriceTotal);
					itemPrice.text(lc_itemPrice);
					var productCount =  $('.num-products-count');
					productCount.text(data.numProducts);
					updateBag();
				},
				error: function(errorData){
					showSnackBar('Oops, something went wrong.');
				}
			});
		} else{
			$input.val(maximum);
			showSnackBar('Maximum quantity reached');
		}	
	});
	
    // Decrement bag value
    $('.minus-button').click(function() {
		var $input = $(this).parents('.input-group').find('.input-group-field');
		var val = parseInt($input.val());
		var $updateForm = $(this).parents('.update-bag-quantity-form');
		var formAction = $updateForm.attr('action');
		var formMethod = $updateForm.attr('method');
		var itemPrice = $(this).parents('.bag-item').find('.item-total');
		var removeForm = $(this).parents('.bag-item').find('.remove-from-bag-form');
		
		if (val > 0){
			$input.val(val - 1);
			var formData = $updateForm.serialize();	
			$.ajax({
				url: formAction,
				method: formMethod,
				data: formData,
				success: function(data){
					showSnackBar(data.messageLoad);
					var itemPriceTotal = data.totalItemPrice;
					lc_itemPrice = toCommas(itemPriceTotal);
					itemPrice.text(lc_itemPrice);
					var productCount =  $('.num-products-count');
					productCount.text(data.numProducts);
					updateBag();
				},
				error: function(errorData){
					showSnackBar('Oops, something went wrong.');
				}
			});
			if ($input.val() == 0){
				// remove item from bag when quantity hits zero
				removeForm.submit();
			}
		} else{
			$input.val(0);
		}
	});

	// update bag details and bag window ajax
    function updateBag(){
        var bagTable = $('.bag-table');
        var bagBody = bagTable.find('.bag-body');
        var currentPath = window.location.href;
        var bagTotal = $('.bag-total');
        var updateBagUrl = '/api/bag/';
        var updateBagMethod = 'GET';
        var data = {};
        $.ajax({
            url: updateBagUrl,
            method: updateBagMethod,
            data: data,
            success: function(data){
                if (data.products.length > 0){
					var total;
					var lc_total;
					total = data.total;
					lc_total = toCommas(total);
                    bagTotal.text(lc_total);
                } else {
                    window.location.href = currentPath;
                }
        	},
        	error: function(errorData){
        		// empty set returned
        	}
		})
	}


})
