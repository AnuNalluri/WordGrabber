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
	console.log("Node number: " + d.id);
	console.log("Node name: " + d.name);
	console.log("Number of outlinks: " + d.outlinks_num);
	console.log("Number of inlinks: " + d.inlinks_num);
	console.log("Number of indegree: " + d.indegree);
	console.log("Number of indegree: " + d.indegree);
	console.log("Number of category: " + d.category);
	console.log("\n");
}

var setLinkWidth = function(d) {
	return Math.min(10, Math.sqrt(d.weight));
}

var setLinkColor = function(d) {
	if (d.source_type == "FAKE" && d.dest_type == "FAKE") {
		return "red";
	} else {
		return "#999";
	}
}

var linkClicked = function(d) {
	console.log("Link source: " + d.source.name);
	console.log("Link target: " + d.target.name);
	console.log("Link source type: " + d.source_type);
	console.log("Link dest type: " + d.dest_type);
	console.log("Link weight: " + d.weight);
	console.log("\n");
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
					.style("stroke", setLinkColor);
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