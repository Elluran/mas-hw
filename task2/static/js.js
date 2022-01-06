var cy = cytoscape({
    container: document.getElementById('cy'), 
    elements: [ 
    ],

    style: [ 
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
            'target-arrow-color': '#b0bec5',
            'target-arrow-shape': 'triangle',
            'arrow-scale' : 2,
            'curve-style': 'bezier'
        }
        }
    ],

    layout: {
        name: 'grid',
        rows: 1
    }

    }); 

setInterval(function() {

    function getRandPos() {
        return Math.random() * 1000
    }

    $.getJSON( "/json/graph", function( data ) {
        data.nodes.forEach(function(elem) {
            cy.add([{ group: 'nodes', data: { id: elem[0], name: elem[0] + "\n" + elem[1]}, position: { x: getRandPos(), y: getRandPos() } }]);
            cy.$('#' + elem[0]).data("name", elem[0] + "\n" + parseFloat(elem[1]).toPrecision(7));
        })
        
        data.edges.forEach(function(elem) {
            cy.add([{ group: 'edges', data: { id: elem[0] + elem[1], source: elem[0], target: elem[1] }} ])
        })


        cy.$('edge').css('line-color', '#cfd8dc');

        data.red_edges.forEach(function(elem) {
            cy.$('#' + elem).css('line-color', '#ef9a9a');
        })
        
        data.green_edges.forEach(function(elem) {
            cy.$('#' + elem).css('line-color', '#81c784');
        })
    });
}, 1000);


$(document).ready(function() {
    $("#run").click(function(){
        cy.$('node').css('background-color', '#4caf50');

        $.ajax({url: "/run", success: function(result){
        $("#div1").html(result);
        }});
    });

    $("#stop").click(function(){
        cy.$('node').css('background-color', '#4caf50');
        $.ajax({url: "/stop", success: function(result){
        }});
    });

    $("#random").click(function(){
        cy.$('edge').css('line-color', '#cfd8dc');
        cy.$('node').css('background-color', '#4caf50');

        $.ajax({url: "/random", success: function(result){
        cy.remove("edge");
        }});
    });

    $("#Agents").change(function(e){
        $.ajax({url: "/set_n/" + $( this ).val(), success: function(result){
            cy.remove("edge");
            cy.remove("node");
        }});
    });

    $("#Range_alpha").change(function(e){
        $.ajax({url: "/set_alpha/" + $( this ).val(), success: function(result){
        }});
    });

    $("#Range_noise").change(function(e){
        $.ajax({url: "/set_noise/" + $( this ).val(), success: function(result){
        }});
    });

    $("#Range_prob").change(function(e){
        $.ajax({url: "/set_prob/" + $( this ).val(), success: function(result){
        }});
    });

    $("#Range_delay").change(function(e){
        $.ajax({url: "/set_delay/" + $( this ).val(), success: function(result){
        }});
    });
});

cy.on('click', 'edge', function(evt){
    var id = this.id()
    $.ajax({url: "/remove_edge/" + this.id(), success: function(result){
        cy.remove("#" + id);
    }});
});

