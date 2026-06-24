let isLoginMode = true;
window.onload = async () => {
    try {
        const r = await fetch('/api/check_login'); const d = await r.json();
        if(d.is_logged_in) {
            const btn = document.getElementById('auth-btn'); btn.innerText = `退出 (${d.username})`;
            btn.onclick = async () => { await fetch('/api/logout'); location.reload(); };
            if(d.is_admin) document.getElementById('admin-nav').style.display='inline';
            else if(d.status==='normal') document.getElementById('apply-btn').style.display='block';
        }
    } catch(e) { console.log("服务器离线"); }
};
window.goPage = (p) => {
    ['home-view','history-view','admin-view'].forEach(id=>document.getElementById(id).style.display='none');
    document.getElementById(p+'-view').style.display='block';
    if(p==='history') loadHistory(); if(p==='admin') loadAdminDashboard();
};
window.startIdentify = async () => {
    const f = document.getElementById('file-input').files[0]; if(!f) return alert("请上传一张狗狗照片");
    const btn = event.target; btn.innerText = "⚡ 分析中..."; btn.disabled = true;
    const fd = new FormData(); fd.append('file', f);
    try {
        const r = await fetch('/predict', {method:'POST', body:fd}); const d = await r.json();
        if(d.success) {
            document.getElementById('res-cn').innerText = d.breed_cn; document.getElementById('res-conf').innerText = d.confidence_pct; document.getElementById('res-en').innerText = d.breed_en;
            document.getElementById('wiki-text').innerHTML = `<p><b>📍 产地：</b>${d.origin}</p><p style="margin-top:10px;"><b>📜 特点：</b>${d.features}</p>`;
            document.getElementById('result-box').style.display = 'flex';
        } else { alert("识别出错: " + d.error); }
    } catch(e) { alert("服务器连接失败，请确保后台程序已运行！"); }
    finally { btn.innerText = "开始智能识别分析"; btn.disabled = false; }
};
window.clickUpload = () => document.getElementById('file-input').click();
window.previewImg = (i) => {
    if(!i.files[0]) return;
    const rd = new FileReader(); rd.onload = (e) => { document.getElementById('img-preview').src=e.target.result; document.getElementById('img-preview').style.display='block'; document.getElementById('upload-hint').style.display='none'; };
    rd.readAsDataURL(i.files[0]);
};
window.openAuthModal = () => document.getElementById('auth-modal').style.display='flex';
window.closeAuthModal = () => document.getElementById('auth-modal').style.display='none';
window.switchAuthMode = () => { isLoginMode=!isLoginMode; document.querySelector('.modal-card h2').innerText=isLoginMode?"用户登录":"用户注册"; };
window.doAuth = async () => {
    const u = document.getElementById('user-in').value; const p = document.getElementById('pass-in').value;
    const res = await fetch(isLoginMode?'/api/login':'/api/register', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u, password:p})});
    const d = await res.json(); if(d.success) location.reload(); else alert(d.message);
};
async function loadAdminDashboard() {
    const s = await (await fetch('/api/admin/stats')).json();
    document.getElementById('stat-users').innerText = s.total_users; document.getElementById('stat-imgs').innerText = s.total_images;
    const l = await (await fetch('/api/admin/all_logs')).json();
    let lh = '<table><tr><th>照片</th><th>用户</th><th>品种</th><th>时间</th></tr>';
    l.data.forEach(x => lh += `<tr><td><img src="/static/uploads/${x.img}" style="width:50px; height:50px; object-fit:cover; border-radius:5px;"></td><td><b>${x.user}</b></td><td>${x.breed}</td><td>${x.time}</td></tr>`);
    document.getElementById('admin-logs').innerHTML = lh + '</table>';
    const p = await (await fetch('/api/admin/pendings')).json();
    let ph = p.data.length ? '<table>' : '暂无申请'; 
    p.data.forEach(u => ph += `<tr><td>${u.name}</td><td><button onclick="approveUser(${u.id})">准许</button></td></tr>`);
    document.getElementById('pending-list').innerHTML = ph + (p.data.length?'</table>':'');
}
window.approveUser = async (uid) => { await fetch('/api/admin/approve', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id: uid})}); loadAdminDashboard(); };
async function loadHistory() {
    const d = await (await fetch('/api/history')).json();
    let h = ''; d.data.forEach(r => h += `<div class="card"><img src="/static/uploads/${r.img}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;"><p style="margin-top:10px;"><b>${r.breed}</b> (${r.conf})</p></div>`);
    document.getElementById('history-grid').innerHTML = h || "无记录";
}
window.applyAdmin = async () => { await fetch('/api/apply_admin', {method:'POST'}); alert("已提交申请"); location.reload(); };