// #ff7f0c
function onClickPlayOrPause(){
    // alert("click play btn");
    d3.select("#circle-5")
        .attr("fill", "#ff7f0c");
}

function onClickForward(){
    if(current_animation_step == 0){
        let start_node = document.getElementById("start-node").value;
        let end_node = document.getElementById("end-node").value;
        let alg_name = document.getElementById("algorithm-selector").value;
        let data_source_name = document.getElementById("data-source-selector").value;
        var formdata = new FormData();
        formdata.append("id", "requestAlg");
        formdata.append("csrfmiddlewaretoken", token);
        formdata.append("start_node", start_node);
        formdata.append("end_node", end_node);
        formdata.append("alg_name", alg_name);
        formdata.append("data_source_name", data_source_name);

        $.ajaxSetup({
            data: {csrfmiddlewaretoken: '{{ csrf_token }}'},
        });

        $.ajax({
            url: "http://127.0.0.1:8000/RouteVisApp1/",
            type: "POST",
            data: formdata,
            processData: false,
            contentType: false,
            success:function (data) {
                jsondata = $.parseJSON(data);
                alg_result = jsondata.alg_result;
                add_list = jsondata.add_list;

                var header_data = ["Round", "Current Set"];
                for(let i = 1; i < add_list.length + 1; ++i){
                    header_data.push("D(" + i.toString() + ")");
                }
                console.log("header_data: \n", header_data);
                var table = d3.select("#detail-area").append("table");
                var header = table.append("thead").append("tr");
                header.selectAll("th")
                    .data(header_data)
                    .enter()
                    .append("th")
                    .text(function(d) {return d;});
                var tablebody = table.append("tbody");
                myArray = [];
                temp_array = [current_animation_step].concat(alg_result[current_animation_step + 1]);
                temp_array[1] = "{ " + add_list.slice(0, current_animation_step + 1).toString() + " }";
                myArray.push(temp_array);
                rows = tablebody
                    .selectAll("tr")
                    .data(myArray)
                    .enter()
                    .append("tr");
                cells = rows.selectAll("td")
                    .data(function(d) {return d;})
                    .enter()
                    .append("td")
                    .text(function(d) {return d;});

                console.log("current set: \n", add_list.slice(0, current_animation_step + 1));
                var node_id = "#circle-" + add_list[current_animation_step].toString();
                console.log("node_id: ", node_id);
                d3.select(node_id)
                    .attr("fill", "#ff7f0c");

                let ratio = (current_animation_step + 1) / add_list.length * 100;
                d3.select("#animation-progress-bar")
                    .attr("style", "width: " + ratio + "%;");

                current_animation_step += 1;
                console.log("current dist: \n", alg_result[current_animation_step]);
            },
            error: function (data) {
                alert("ajax Exception! requestAlg Wrong!");
            }
        });

    }else{
        if(current_animation_step < add_list.length){
            node_id = "#circle-" + add_list[current_animation_step].toString();
            console.log("node_id: ", node_id);
            d3.select(node_id)
            .attr("fill", "#ff7f0c");

            temp_array = [current_animation_step].concat(alg_result[current_animation_step + 1]);
            temp_array[1] = "{ " + add_list.slice(0, current_animation_step + 1).toString() + " }";
            myArray.push(temp_array);
            tablebody = d3.select("tbody");
            rows = tablebody
                .selectAll("tr")
                .data(myArray)
                .enter()
                .append("tr");
            cells = rows.selectAll("td")
                .data(function(d) {return d;})
                .enter()
                .append("td")
                .text(function(d) {return d;});

            let ratio = (current_animation_step + 1) / add_list.length * 100;
            d3.select("#animation-progress-bar")
                .attr("style", "width: " + ratio + "%;");

            console.log("current set: \n", add_list.slice(0, current_animation_step + 1));
            current_animation_step += 1;
            console.log("current dist: \n", alg_result[current_animation_step]);
        }else{
            current_animation_step += 1;
            if(current_animation_step == add_list.length + 2){
                window.location.reload(false);
            }
        }
    }
}