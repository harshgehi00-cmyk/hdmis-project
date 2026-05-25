function sendMessage(){

    let input = document.getElementById("chat-input").value;

    let response = "";

    input = input.toLowerCase();

    if(input.includes("fever")){

        response = "Possible viral infection detected.";

    }

    else if(input.includes("headache")){

        response = "Please drink water and consult doctor.";

    }

    else if(input.includes("appointment")){

        response = "You can book appointment from dashboard.";

    }

    else{

        response = "Please consult hospital specialist.";
    }

    document.getElementById("chat-response").innerHTML = response;
}