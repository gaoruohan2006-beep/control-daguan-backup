const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const katex=require(path.join(root,'public/vendor/katex/katex.min.js'));
const bank=JSON.parse(fs.readFileSync(path.join(root,'public/data/library.json'),'utf8'));
let count=0,errors=[];
for(const q of bank.questions){
  const detail=JSON.parse(fs.readFileSync(path.join(root,`public/data/questions/${q.id}.json`),'utf8'));
  for(const [field,text] of Object.entries({stem:q.stem,answer:detail.answer,explanation:detail.explanation})){
    for(const m of text.matchAll(/\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g)){
      count++;
      try{katex.renderToString(m[1]||m[2],{displayMode:!!m[1],throwOnError:true,strict:false});}
      catch(e){errors.push({id:q.id,number:q.number,source:q.source,field,tex:m[1]||m[2],error:e.message});}
    }
  }
}
console.log(JSON.stringify({formulas:count,errors},null,2));
if(errors.length)process.exitCode=1;
