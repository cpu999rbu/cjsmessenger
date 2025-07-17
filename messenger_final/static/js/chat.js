const ws=new WebSocket(`ws://${location.host}/ws`);
ws.onopen=()=>ws.send(JSON.stringify({type:'status',user:document.body.dataset.user,online:true}));
ws.onmessage=e=>{const msg=JSON.parse(e.data);
 if(msg.type==='status'){document.getElementById(`status-${msg.user_id}`).innerText=msg.online?'• online':'• offline';}
 if(msg.type==='typing'){const ind=document.getElementById(`typing-${msg.user_id}`);ind.innerText=msg.typing?`${msg.user_name} печатает...`:'';}
};
window.sendMessage=(evt,recipient)=>{evt.preventDefault();const text=document.getElementById('msg-input').value;ws.send(JSON.stringify({type:'message',to:recipient,text}));document.getElementById('msg-input').value='';return false;};
window.typing=(recipient)=>{ws.send(JSON.stringify({type:'typing',to:recipient}));};