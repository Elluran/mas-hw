var cy = cytoscape({
    container: document.getElementById('cy'), // container to render in
    elements: [ // list of graph elements to start with
    ],

    style: [ // the stylesheet for the graph
        {
        selector: 'node',
        style: {
            'text-wrap': 'wrap',
            'label': "data(name)",
            'background-color': '#4caf50',
        }
        },

        {
        selector: 'edge',
        style: {
            'width': 3,
            'line-color': '#cfd8dc',
            'target-arrow-color': '#cfd8dc',
            // 'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
        }
        }
    ],

    layout: {
        name: 'grid',
        rows: 1
    }

    }); 

PERIOD = 1000

setInterval(function() {

    $.getJSON( "/json/graph", function( data ) {
        data.red.forEach(function(elem) {
            cy.$('#n' + elem).css('background-color', '#dd2c00');
        })
        
        data.grey.forEach(function(elem) {
            cy.$('#n' + elem).css('background-color', '#212121');
        })

        function randPos() {
            p = Math.random() * 360. * Math.PI / 180.;
            return {x: Math.cos(p) * 300 + Math.random() * 100 + 500, y: Math.sin(p) * 300 + Math.random() * 100 + 500}
        }

        data.nodes.forEach(function(elem) {
            cy.add([{ group: 'nodes', data: { id: elem[0], name: elem[0] + "\n" + elem[1]}, position: randPos() }]);
            cy.$('#' + elem[0]).data("name", elem[0] + "\n" + elem[1]);
        })
        
        data.edges.forEach(function(elem) {
            cy.add([{ group: 'edges', data: { id: elem[0] + elem[1], source: elem[0], target: elem[1] }} ])
        })
    });

    $.getJSON( "/json/answer", function( data ) {
        if(data.answer != '?') {
            $('#answer').val(data.answer)
        }
    });
}, PERIOD);


$(document).ready(function() {
    $("#run").click(function(){
        cy.$('node').css('background-color', '#4caf50');

        $.ajax({url: "/run", success: function(result){
        $("#div1").html(result);
        }});
    });

    $("#reset").click(function(){
        cy.$('node').css('background-color', '#4caf50');

        $.ajax({url: "/reset", success: function(result){
        $("#div1").html(result);
        }});
    });

    $("#random").click(function(){
        cy.$('node').css('background-color', '#4caf50');

        $.ajax({url: "/random", success: function(result){
        $("#div1").html(result);
        cy.remove("edge");
        }});
    });

    $("#Agents").change(function(e){
        $.ajax({url: "/set_n/" + $( this ).val(), success: function(result){
            cy.remove("edge");
            cy.remove("node");
        }});
    });

    cy.on('click', 'edge', function(evt){
        var id = this.id()
        $.ajax({url: "/remove_edge/" + this.id(), success: function(result){
            cy.remove("#" + id);
        }});
    });
});



