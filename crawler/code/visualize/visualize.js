var width = 960;
var height = 600;

var zoomed = function() {
	node.attr("transform", d3.event.transform);
}

var setNodeRadius = function(d) {
	return Math.sqrt(d.inlinks_num);
}

var setNodeText = function(d) {
	return d.name;
}

var setNodeTextSize = function(d) {
	return 12;
}

var setNodeColor = function(d) {
	if (d.category == "OTHER") {
		return "green";
	} else if (d.category == "REAL") {
		return "yellow";
	} else if (d.category == "FAKE") {
		return "red";
	} else if (d.category == "SOCIAL") {
		return "blue";
	} else {
		return "black";
	}
}

var nodeClicked = function(d) {
	alert("Node number: " + d.id  + "\n" +
		"Node name: " + d.name + "\n" +
		"Number of outlinks: " + d.outlinks_num + "\n" +
		"Number of inlinks: " + d.inlinks_num + "\n" +
		"Number of outdegree: " + d.outdegree + "\n" +
		"Number of indegree: " + d.indegree + "\n" +
		"Category: " + d.category);
}

var setLinkWidth = function(d) {
	return Math.sqrt(d.weight);
}

var setLinkColor = function(d) {
	if (d.source_type == "FAKE" && d.dest_type == "FAKE") {
		return "red";
	} else {
		return "white";
	}
}

var linkClicked = function(d) {
	alert(
	"Link source: " + d.source.name + "\n" +
	"Link target: " + d.target.name + "\n" +
	"Link source type: " + d.source_type + "\n" +
	"Link dest type: " + d.dest_type + "\n" +
	"Link weight: " + d.weight
	);
}

var canvas = d3.select("svg"),
        width = +canvas.attr("width"),
        height = +canvas.attr("height"),
        node,
        link;

var g = canvas.append("g");

canvas.call(d3.zoom().on("zoom", function() {
		g.attr("transform", d3.event.transform);
	}));

var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function (d) {return d.id;}).distance(1000).strength(1))
        .force("center", d3.forceCenter(document.body.clientWidth / 2, document.body.clientHeight / 2));

var loadJSON = function(error, json) {
	if (error) throw error;

	var link = g.selectAll(".link")
					.data(json.links)
					.enter()
					.append("line")
					.attr("class", "link")
					.style("stroke-width", setLinkWidth)
					.style("stroke", setLinkColor);

	var node = g.selectAll(".node")
					.data(json.nodes)
					.enter()
					.append("g")
					.attr("class", "node")
					.call(d3.drag()
							.on("start", dragstarted)
							.on("drag", dragged)
					);
	g.selectAll(".node").on('click', nodeClicked);
	g.selectAll(".link").on('click', linkClicked);

	node.append("circle")
		.attr("r", setNodeRadius)
		.style("fill", setNodeColor);

	node.append("text")
		.attr("text-anchor", "middle")
		.text(setNodeText)
		.attr('font-size', setNodeTextSize);

	function ticked() {
        link
		.attr("x1", function (d) {return d.source.x;})
		.attr("y1", function (d) {return d.source.y;})
		.attr("x2", function (d) {return d.target.x;})
		.attr("y2", function (d) {return d.target.y;});

        node.attr("transform", function (d) {return "translate(" + d.x + ", " + d.y + ")";});
    }

	simulation.nodes(json.nodes)
				.on("tick", ticked);

	simulation.force("link")
				.links(json.links);
}

var dragstarted = function(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

var dragged = function(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

d3.json("data.json", loadJSON);