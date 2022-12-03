var express = require('express');
var bodyParser = require('body-parser');
var app = express();
app.use(express.text())
const textparser=bodyParser.text({extended:false})
app.use(bodyParser.text());
var port = 9000;

app.post('/post/data',textparser ,function(req, res) {
    console.log('receiving data...');
    console.log('body is ',req.body);
    const arr=req.body

    arr.toString().toLowerCase();
    console.log(arr)
    const splitstr=arr.split(" ")
    for (i=0;i<splitstr.length;i++){
    const arr= ["hi","hello","hey","helloo","helloo","hello!","hey man"]
    const productlist=["Almasons GINI platform","Gini Voice recognition","eSign for supply chain"]
        console.log(splitstr[i])
        var mydate=new Date();
        var hrs=mydate.getHours();


        
            

        arr.forEach(element=>{
            if (splitstr[i]==element){
                
                if(hrs<12){
                    res.send(`hello good morning how can i help you `)
                }
                else if (hrs>=12 && hrs <=17){
                    res.send("hello good afternoon how can i help you")
                }
                else if (hrs>=17 && hrs <=20){
                    res.send(`hello good evening how can i help you `)
                }
                else{
                    res.send("hello good night how can i help you")
                }
                  
            }
        })
       
    }

    // console.log(arr)
    //arr.split()
    // console.log(arr.split())
    // const{climate}=req.body
    // console.log(climate)
    // res.send(`todays climate is too ${climate}`)
});

// start the server
app.listen(port);
console.log('Server started! At http://localhost:' + port);