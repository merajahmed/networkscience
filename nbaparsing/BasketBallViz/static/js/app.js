/**
 * Created by meraj on 4/25/16.
 */
graphstats = null;
$(document).ready(function(){

    $.getJSON('static/gamelist.json',function(result){
        var options = $("#game_id");
        $.each(result.games, function(){
            var option = $('<option />');
            option.attr('value', this.gameid).text(this.name);
            $('#game_id').append(option);
        });
    });
    $('#game_id').change(function () {
       graph($('#game_id').val()+'.json');
    });
});

function graph(name){
       $.getJSON('static/visgraphs/'+name, function(graph_data){

        var nodes = graph_data['nodes'];
        var edges = graph_data['edges'];
        var container = document.getElementById('mynetwork');
        var data = {
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges)
        };

        var start_group = {'color':'#55aa55'};
        var end_group = {'color':'#d46a6a'};
        var player_group = {'color':'#669999'};
        var groups = {'start':start_group, 'end':end_group, 'players':player_group};
        var options = {'groups':groups};
        var network = new vis.Network(container, data, options);
        network.on("click", function (params) {
            //params.event = "[original event]";
            //document.getElementById('eventSpan').innerHTML = '<h2>Click event:</h2>' + JSON.stringify(params, null, 4);
            //edges = params.edges;
            nodes = params.nodes;
            $('#playerstats').html("Player Stats:-" +"<br/>"+
                "Degree Centrality: "+graphstats['centrality'][nodes[0]]+"<br/>"+
                "Clustering Coefficient: "+graphstats['clustering'][nodes[0]]);
        });

    });
    $.getJSON('static/stats/'+name, function(stats){
        graphstats = stats;
        var teamcentrality = stats['teamcentrality'];
        var entropy = stats['entropy'];
        var flux = stats['flux'];
        var centralplayer = stats['centralplayer'];
        $('#teamstats').html("Team Stats:-" +"<br/>"+
            "Team Centrality: "+teamcentrality+"<br/>"+
        "Flux: "+flux+"<br/>"+
        "Entropy: "+entropy+"<br/>"+
        "Central Player: "+centralplayer);
    });

}