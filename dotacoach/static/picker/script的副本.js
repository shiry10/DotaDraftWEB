
$(document).ready(function(){
  var clickEnabled = true;

  // update the options
  $("#start").click(
    function(){
      var side = $("#side_select :selected").val();
      var level = $("#level_select :selected").val();
      $("#side_value").val(side);
      $("#level_value").val(level);
      // reset selected hero
      $("#pre_selected_radiant").val("");
      $("#pre_selected_dire").val("");
      $("#round_number").val('0');
      // show side and level
      var side_text = "";
      if (side === '0') { side_text = 'radiant'; } else { side_text = 'dire'; }
      // $(".information").text(`Your side: ${side_text}. Bot level: ${level}. `);
      // bot select if bot first
      bot_select(side, level);
    }
  )


  // select hero for bot given side and level
  // select until player's turn
  function bot_select(player_side, level) {
    // get data from webpage
    var bot_side;
    if (player_side==='0') {bot_side = '1';} else {bot_side = '0';}
    var pick_order = $("#pick_order").val();
    var round_number = parseInt($("#round_number").val());
    data = {};
    data['bot_side'] = bot_side;
    data['level'] = level;
    data['pick_order'] = pick_order;
    // do select if bot's turn
    while (round_number<10) {
      // wait 1 second
      // update data
      data['round_number'] = round_number;
      data['pre_selected_radiant'] = $("#pre_selected_radiant").val();
      data['pre_selected_dire'] = $("#pre_selected_dire").val();
      // if not bot's turn, do nothing but enable click and break
      if (pick_order[round_number] != data['bot_side']) {
        $.ajax({
          url: bot_select_url,
          method: 'GET',
          data: data,
          success: function(ret){
            alert('a');
            clickEnabled = true;
          }
        })
        break;
      }
      // choose hero for bot
      $.ajax({
        url: bot_select_url,
        method: 'GET',
        data: data,
        // async: false,
        success: function(ret){
          var bot_selected_hero = ret['bot_selected_hero'];
          var radiant_selected = ret['radiant_selected'];
          var dire_selected = ret['dire_selected'];
          var round_number = parseInt(ret['round_number']);
          var bot_side = ret['bot_side'];
          var pick_order = $("#pick_order").val();
          // update the page
          $(document.getElementById(`button_${bot_selected_hero}`)).attr('disabled','disabled');
          $("#pre_selected_radiant").val(radiant_selected);
          $("#pre_selected_dire").val(dire_selected);
          $("#round_number").val((round_number+1));
          // update image of the target slot
          var pos = find_pos(bot_side, pick_order, round_number);
          var image_path = $(document.getElementById(`image_${bot_selected_hero}`)).attr("src");
          if (bot_side==='0') {
            $(`#radiant_selected_${pos}_image`).attr("src",image_path);
          } else {
            $(`#dire_selected_${pos}_image`).attr("src",image_path);
          }
          clickEnabled = true;
        }
      })
      // update while loop:
      round_number++;
    }
    if (round_number===10) {
      show_result();
    }
  }



  // player select hero
  $(".single").click(function(){
    if (!clickEnabled) {
      return;
    }
    clickEnabled = false;
    var side = $("#side_value").val();
    var level = $("#level_value").val();
    // if no side and level, do nothing
    if (!['0', '1'].includes(side) || !['easy', 'medium', 'hard'].includes(level)) {
      $(".information").text('Please select your side and bot level. ');
      return;
    }
    // if heroes are all set, do nothing
    if (parseInt($("#round_number").val()) >= 10) {
      return;
    }
    // get essential information
    var pick_order = $("#pick_order").val();
    var round_number = $("#round_number").val();
    // get data from the click action
    // including: hero clicked, selected hero of two teams,
    var cur_selected = $(this).val();
    var pre_selected_radiant = $("#pre_selected_radiant").val();
    var pre_selected_dire = $("#pre_selected_dire").val();
    // update two teams
    if (side==='0') {
      pre_selected_radiant = pre_selected_radiant + ',' + cur_selected;
      $("#pre_selected_radiant").val(pre_selected_radiant); // update team data
      // update image of the target slot
      var pos = find_pos(side, pick_order, round_number);
      var image_path = $("img", this)[0].getAttribute("src");
      $(`#radiant_selected_${pos}_image`).attr("src",image_path);
    }
    if (side==='1') {
      pre_selected_dire = pre_selected_dire + ',' + cur_selected;
      $("#pre_selected_dire").val(pre_selected_dire);
      // update image of the target slot
      var pos = find_pos(side, pick_order, round_number);
      var image_path = $("img", this)[0].getAttribute("src");
      $(`#dire_selected_${pos}_image`).attr("src",image_path);
    }
    // disable this clicked hero to prevent the repeat selection.
    $(this).attr('disabled','disabled');
    // update round_number
    round_number++;
    $("#round_number").val(round_number);
    if (round_number===10) {
      show_result();
    }
    // if next is bot's turn, select for bot. If not, end.
    bot_select(side, level);
  })


function show_result() {
  // if all ten heroes are selected, show the result.
  data = {};
  data['pre_selected_radiant'] = $("#pre_selected_radiant").val();
  data['pre_selected_dire'] = $("#pre_selected_dire").val();
  $.ajax({
    url: result_url,
    method: 'GET',
    data: data,
    success: function(ret){
      var result = ret['win_team'];
      if (result==='0') {
        $("#result").text('RADIANT VICTORY');
        $("#result").css("background-color","#004d00");
      } else {
        $("#result").text('DIRE VICTORY');
        $("#result").css("background-color","#4d0000");
      }
    }
  })
}



function find_pos(side, pick_order, round_number) {
  var pos = 0;
  var i = 0;
  while (i <= round_number) {
    if (pick_order[i]===side) { pos++; }
    i++;
  }
  return pos;
}



})
