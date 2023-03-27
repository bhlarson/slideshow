/*
# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# top-level README.md file.
# ==============================================================================
*/

var endpoint;
var bot;
var context = {};
var payload = {};
var scrollToBottomTime = 500;
var infoTextArea; //element for context display
var debug = false; //if true display context
var user_conversation_index = null;
var socket =  null;

function getTimeSting() {
  var d = new Date();
  var ampm = "";
  var h = d.getHours();
  var m = d.getMinutes();
  if (h==0) {
	  h = "12"; ampm = "am";
  } else if (h<12) {
	  ampm = "am";
  } else if (h==12) {
	  ampm = "pm";
  } else {
	  h = h-12; ampm = "pm";
  }
  if (m>=0 && m<=9) {
	  m = "0" + m
  }
  return h + ":" + m + " " + ampm;
}


// ---------------------------------------------------------------------------------------
// Show text message
// ---------------------------------------------------------------------------------------
function showUserMessage(text) {
  console.log("showSystemMessages: " + text);

  let user_text  = document.createElement('div')
  user_text.innerHTML = text

  var user_img = document.createElement("img");
  user_img.setAttribute("class","profile_picture_left" )
  user_img.src = "img/user.png";

  let user_time  = document.createElement('span')
  user_time.setAttribute("class", "balon2user p-2 m-0 position-relative")
  user_time.textContent = 'You - ' + getTimeSting();

  let balloon  = document.createElement('a')
  balloon.setAttribute("class","float-left" )
  balloon.append(user_img)
  balloon.append(user_time)
  balloon.append(user_text)

  let msg  = document.createElement('div')
  msg.setAttribute("class", "balon2 p-2 m-0 position-relative")
  msg.appendChild(balloon)

  var elem = document.getElementById('communication_area');
  elem.append(msg);
  // scroll to bottom of page
  elem.scrollTop = elem.scrollHeight;
}

var iBallonImg = 0;
var iBallonTime = 1;
var iBallonEdit = 2;
var iBallonEditData = 3;
var iBallonAnswer = 4;
var iBallonGTAnswer = 5;

function Edit(question, answer, balloon, button)
{
  // var children = balloon.children;
  // balloon.removeChild(balloon.children[2]);
  if (button.innerHTML == 'Edit'){
    button.innerHTML = 'Submit';

    var text_edit = document.createElement('textarea');
    text_edit.setAttribute("class", "editanswer")
    text_edit.value = answer
    balloon.append(text_edit)
  }
  else{

    const params = {
      question: question.replace(/</g, "&lt;"),
      answer: answer.replace(/</g, "&lt;"),
      correct_answer: balloon.lastElementChild.value.replace(/</g, "&lt;")
    };

    const options = {
      method: 'PUT',
      headers: {'Content-type': 'application/json'},
      body: JSON.stringify( params )  
    }; 

    fetch('/addqa', options)
    .then(function (response) {
        return response.json();
    }).then(function (results) {
        distance = parseFloat( results.answer_distance).toFixed(5)
        console.log('/addqa error: ' + distance);
        balloon.children[iBallonEditData].textContent = '\u0394: ' + distance;
    });

    button.innerHTML = 'Edit';
    balloon.removeChild(balloon.lastElementChild)
  }

}

// ---------------------------------------------------------------------------------------
// Shows message of user
// ---------------------------------------------------------------------------------------
function showKSMessage(question, answer) {
  // escape html tags
  answer = answer.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  let user_text  = document.createElement('div')
  user_text.innerHTML = answer

  var user_img = document.createElement("img");
  user_img.setAttribute("class","profile_picture_right" )
  user_img.src = "img/bot.svg";

  let user_time  = document.createElement('span')
  user_time.setAttribute("class", "balon1user p-2 m-0 position-relative")
  user_time.textContent = 'KSB - ' + getTimeSting();

  let balloon  = document.createElement('a')

  var edit = document.createElement('button');
  edit.setAttribute("class", "correct p-2 m-0 position-relative")
  edit.innerHTML = 'Edit';
  edit.addEventListener("click", function(){Edit(question, answer, balloon, edit);});

  let edit_data  = document.createElement('span')
  edit_data.setAttribute("class", "balon1user p-2 m-0 position-relative")
  edit_data.textContent = '';


  balloon.setAttribute("class","float-right" )
  balloon.append(user_img)
  balloon.append(user_time)
  balloon.append(edit)
  balloon.append(edit_data)
  balloon.append(user_text)

  let msg  = document.createElement('div')
  msg.setAttribute("class", "balon1 p-2 m-0 position-relative")
  msg.appendChild(balloon)

  var elem = document.getElementById('communication_area');
	elem.append(msg);
	// scroll to bottom of page
  elem.scrollTop = elem.scrollHeight;
}

function getBrowser() {
	if(navigator.userAgent.indexOf("Chrome") != -1 ) {
		browser = 'Chrome';
    }
    else if(navigator.userAgent.indexOf("Safari") != -1) {
    	browser = 'Safari';
    }
    else if(navigator.userAgent.indexOf("Firefox") != -1 ) {
    	browser = 'Firefox';
    }
}

// ---------------------------------------------------------------------------------------
// Gets parameter by name
// ---------------------------------------------------------------------------------------
function getParameterByName(name, url) {
  let arr = url.split("#");
  let match = RegExp("[?&]" + name + "=([^&]*)").exec(arr[0]);
  return match && decodeURIComponent(match[1].replace(/\+/g, " "));
}


(function() {
    socket =  io();
    socket.on('connect', function() {
      socket.emit('my event', {data: 'I\'m connected!'});
  });
})();




// ---------------------------------------------------------------------------------------
// Click on submit button
// ---------------------------------------------------------------------------------------

function Ask() {

  showUserMessage([document.getElementById('question_input').value])

  const params = {
      question: document.getElementById('question_input').value,
  };

  document.getElementById('question_input').value = ""
  
  const options = {
      method: 'PUT',
      headers: {'Content-type': 'application/json'},
      body: JSON.stringify( params )  
  }; 

  fetch('/ask', options)
  .then(function (response) {
      return response.json();
  }).then(function (status) {
      showKSMessage(params.question, status.response)
      console.log('/ask request: ' + params.question);
      console.log('/ask response: ' + status.response);
  });
}