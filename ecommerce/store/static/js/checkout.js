var form = document.getElementById('shipping-form');

form.addEventListener('submit', function(e){
    e.preventDefault();
    console.log('Form Submitted...');
    document.getElementById('form-button').style.display = 'none';

    var shippingInfo = {
        'address': form.address.value,
        'city': form.city.value,
        'region': form.region.value,
        'zipcode': form.zipcode.value,
    };

    var orderId = "{{ order.id }}";
    var csrfToken = "{{ csrf_token }}";

    var url = '/process_order/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'orderId': orderId,
            'shippingInfo': shippingInfo,
        })
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Success:', data);
        alert('Transaction completed!');
        window.location.href = "{% url 'store' %}";
    });
});