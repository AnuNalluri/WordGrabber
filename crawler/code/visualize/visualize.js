var width = 960;
var height = 600;

var zoomed = function() {
	console.log("zoomed!");
	node.attr("transform", d3.event.transform);
}

var setNodeRadius = function(d) {
	if (d.color == "blue") {
		return 3;
	} else if (d.color == "red") {
		return 20
	}
	return 10;
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
	return Math.min(10, Math.sqrt(d.weight));
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

canvas.append('defs').append('marker')
	.attrs({'id':'arrowhead',
		'viewBox':'-0 -5 10 10',
		'refX':13,
		'refY':0,
		'orient':'auto',
		'markerWidth':5,
		'markerHeight':5,
		'xoverflow':'visible'})
	.append('svg:path')
	.attr('d', 'M 0,-5 L 10 ,0 L 0,5')
	.attr('fill', '#999')
	.style('stroke','none');

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
					.attr("stroke", "black")
					.attr("marker-end", "url(#arrowhead)");

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
		.attr("y2", function (d) {return d.target.y;})
		.attr("d", function(d) {
            // Total difference in x and y from source to target
            diffX = d.target.x - d.source.x;
            diffY = d.target.y - d.source.y;

            // Length of path from center of source node to center of target node
            pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

            // x and y distances from center to outside edge of target node
            offsetX = (diffX * d.target.radius) / pathLength;
            offsetY = (diffY * d.target.radius) / pathLength;

            return "M" + d.source.x + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY);
        });

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