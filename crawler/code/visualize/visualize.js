var width = 960;
var height = 600;

var zoomed = function() {
	console.log("zoomed!");
	node.attr("transform", d3.event.transform);
}

var setNodeRadius = function(d) {
	return Math.min(100, Math.max(5, d.size));
}

var setNodeText = function(d) {
	return d.name;
}

var setNodeTextSize = function(d) {
	return Math.min(15, d.size / 12);
}

var setNodeColor = function(d) {
	return d.color;
}

var setLinkWidth = function(d) {
	return Math.sqrt(d.weight);
}

var canvas = d3.select("svg"),
        width = +canvas.attr("width"),
        height = +canvas.attr("height"),
        node,
        link;

var g = canvas.append("g");

canvas.call(d3.zoom().on("zoom", function() {
		console.log("zoomed!");
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
					.style("stroke-width", setLinkWidth);

	var node = g.selectAll(".node")
					.data(json.nodes)
					.enter()
					.append("g")
					.attr("class", "node")
					.call(d3.drag()
							.on("start", dragstarted)
							.on("drag", dragged)
					);
	

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