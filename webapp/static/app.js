// 1-image-at-a-time endpoint 
var filteredUrl = "/data/?filter=True";

// make label query (e.g. 0,1,2)
d3.json("/labels.json", function(labels) {
    // pass the row selection here, PUT the corresponding label or button id
    var updateData = function(selection, label) {
        var rowData = selection.data()[0];
        var rdata = JSON.stringify({id: rowData.id, label_id: label})
        d3.request("/data/" + rowData.id + ".json")
            .send("PUT", rdata, function(response) {
                d3.json(filteredUrl, processData);
            });
    };

    // paint the page elements, bind with incoming data 
    var processData = function(data) {
        // if an image row already exists, clear it
        d3.select("#container").selectAll("*").remove();
        // hierarchy: container => row => 3 x col-md-4 (columns) 
        var row = d3.select("#container")
            .selectAll(".row")
            .data(data)
            .enter()
            .append("div");
        row.classed("row", true);

        // col 1: image
        var images = row.append("div")
        images.classed("col-md-4", true)
            .append("img")
            .classed("img-responsive", true)
            .attr("src", function(d) { return d.link; });

        // col 2: list of predictions (and scores)
        var predictions = row.append("div")
        predictions.classed("col-md-4", true);
        predictions.append("ol")
            .selectAll("li")
            .data(function(d) { return d.predictions;})
            .enter()
            .append("li")
            .text(function(d) { return d[0] + " : " + d[1];});

        // col 3: buttons for selection
        var buttonCol = row.append("div")
        buttonCol.classed("col-md-4", true)
        var buttons = buttonCol.selectAll("button")
            .data(labels)
            .enter()
            .append("button") 
            .classed("btn btn-primary btn-lg", true)
            .text(function(d) { return d.name; });

        // update db on click selection 
        buttons.on("click", function(d) {
            // set button state to "active"
            d3.select(this).classed("active focus", true);
            updateData(d3.select(this.parentElement), d.id);
        });
        
        // update db on specific button press (faster than clicking)
        d3.select("body").on("keydown", function(e) {
            var rowSelection = d3.select(".row");
            switch (d3.event.key) {
                // hard-code the label ids for now (0=top1, 1=top5, 2=None)
                case "j": updateData(rowSelection, 0); break;
                case "k": updateData(rowSelection, 1); break;
                case "l": updateData(rowSelection, 2); break;
            }
        });
    };

    // make data query
    d3.json(filteredUrl, processData);
});

