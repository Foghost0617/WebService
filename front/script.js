// script.js

// ------------------------------------------------------------------
// 配置
// ------------------------------------------------------------------
const API_BASE_URL = 'http://127.0.0.1:8000/personnel';

// DOM 元素引用
const form = document.getElementById('personnelForm');
const tableBody = document.querySelector('#personnelTable tbody');
const messageDisplay = document.getElementById('message');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');
const formTitle = document.getElementById('formTitle');
const isEditingInput = document.getElementById('isEditing');
const originalStudentIdInput = document.getElementById('originalStudentId');


function formatTime(timeStr) {
    if (!timeStr) return '';
    return new Date(timeStr).toLocaleString('zh-CN', { 
        year: 'numeric', month: '2-digit', day: '2-digit', 
        hour: '2-digit', minute: '2-digit', second: '2-digit' 
    });
}

/**
 * 显示操作消息/错误
 * @param {string} msg 消息内容
 * @param {boolean} isError 是否为错误信息
 */
function displayMessage(msg, isError = false) {
    messageDisplay.textContent = msg;
    messageDisplay.className = isError ? 'message-area error' : 'message-area success';
    // 错误信息将保持显示，直到下一次操作或用户点击取消按钮。
}

async function apiRequest(url, method, data = null) {
    const headers = { 'Content-Type': 'application/json' };
    
    const config = {
        method: method,
        headers: headers,
        body: data ? JSON.stringify(data) : null
    };

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const responseText = await response.text();
            
            let errorMessage = `请求失败 (状态码: ${response.status})。`; 
            
            try {
                const errorData = JSON.parse(responseText);
                
                if (response.status === 422 && Array.isArray(errorData.detail)) {
                    const validationErrors = errorData.detail.map(err => {
                        const cleanedMsg = err.msg.replace(/Value error, /g, ''); 
                        if (cleanedMsg.includes('must be a valid string') || cleanedMsg.includes('value is not a valid string')) {
                             return `字段类型错误: ${err.loc[1]}`;
                        }
                        return cleanedMsg;
                    }).join('; ');
                    errorMessage = `${validationErrors}`; 

                } else if (errorData.detail) {
                    // 409/404 或其他 HTTPException 错误
                    errorMessage = (typeof errorData.detail === 'string') ? errorData.detail : '后端返回了复杂的错误对象。';
                    if (typeof errorData.detail !== 'string') {
                         console.error('后端返回的原始错误:', errorData.detail);
                    }
                } else {
                    errorMessage += `原始错误体: ${responseText}`;
                }

            } catch (e) {
                errorMessage += `后端响应文本: ${responseText}`;
            }

            throw new Error(errorMessage);
        }
        
        // DELETE (204) 和其他无内容响应
        if (response.status === 204 || response.headers.get('content-length') === '0') {
            return null;
        }

        return await response.json();
    } catch (error) {
        const displayMsg = `操作失败: ${error.message}`;
        
        console.error(`API 请求失败 (${method} ${url}):`, error.message);
        displayMessage(displayMsg, true); 
        
        throw error; 
    }
}


/**
 * 获取人员列表 (GET /personnel)
 */
async function fetchPersonnelData() {
    tableBody.innerHTML = '<tr><td colspan="7">加载中...</td></tr>';
    try {
        const data = await apiRequest(`${API_BASE_URL}/?mode=descend`, 'GET');
        renderTable(data.items || []);
    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="7">加载失败，请检查后端是否运行。</td></tr>';
    }
}

/**
 * 新增或修改人员 (POST /personnel 或 PUT /personnel/{id})
 */
async function submitPersonnel(event) {
    event.preventDefault(); 

    submitBtn.disabled = true;
    submitBtn.textContent = '处理中...';

    const data = {
        id: document.getElementById('id').value,
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        tel: document.getElementById('tel').value,
        hobby: document.getElementById('hobby').value || null
    };

    const isEdit = isEditingInput.value === 'true';
    const originalId = originalStudentIdInput.value;
    let result;

    try {
        if (isEdit) {
            const url = `${API_BASE_URL}/${originalId}`;
            result = await apiRequest(url, 'PUT', data);
        } else {
            const url = `${API_BASE_URL}/`;
            result = await apiRequest(url, 'POST', data);
        }

        if (result) {
            displayMessage(isEdit ? '修改成功！' : '新增成功！', false);
            form.reset();
            resetFormState(); 
            fetchPersonnelData(); 
        }
    } catch (e) {
        // apiRequest 会处理错误显示
    } finally {
        // 恢复按钮状态
        submitBtn.disabled = false;
        submitBtn.textContent = isEdit ? '保存修改' : '新增';
    }
}

/**
 * 删除人员 (DELETE /personnel/{id})
 */
async function deletePersonnel(studentId, name) {
    if (!confirm(`确定要删除人员【${name}】 (学号: ${studentId}) 吗？此操作不可撤销！`)) {
        return;
    }
    const url = `${API_BASE_URL}/${studentId}`;
    try {
        await apiRequest(url, 'DELETE');
        displayMessage(`人员【${name}】删除成功！`, false);
        fetchPersonnelData();
    } catch (e) {
        // apiRequest 会处理错误显示
    }
}

// ------------------------------------------------------------------
// 表格渲染与交互
// ------------------------------------------------------------------

/**
 * 渲染表格数据
 */
function renderTable(personnelList) {
    tableBody.innerHTML = '';
    if (personnelList.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">没有找到任何记录。</td></tr>';
        return;
    }

    personnelList.forEach(person => {
        const row = tableBody.insertRow();
        
        row.insertCell().textContent = person.id;
        row.insertCell().textContent = person.name;
        row.insertCell().textContent = person.tel;
        row.insertCell().textContent = person.email;
        row.insertCell().textContent = person.hobby || '-';
        row.insertCell().textContent = formatTime(person.created_time);
        
        const actionCell = row.insertCell();
        
        // 修改按钮
        const editBtn = document.createElement('button');
        editBtn.textContent = '修改';
        editBtn.className = 'btn btn-secondary';
        editBtn.onclick = () => loadForEdit(person);
        actionCell.appendChild(editBtn);

        // 删除按钮
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '删除';
        deleteBtn.className = 'btn btn-danger';
        deleteBtn.style.marginLeft = '10px';
        deleteBtn.onclick = () => deletePersonnel(person.id, person.name);
        actionCell.appendChild(deleteBtn);
    });
}

/**
 * 加载数据到表单，准备修改*/
function loadForEdit(person) {
    document.getElementById('id').value = person.id;
    document.getElementById('name').value = person.name;
    document.getElementById('email').value = person.email;
    document.getElementById('tel').value = person.tel;
    document.getElementById('hobby').value = person.hobby;
    
    // 设置编辑状态
    isEditingInput.value = 'true';
    originalStudentIdInput.value = person.id; 
    
    document.getElementById('id').disabled = false; 
    
    submitBtn.textContent = '保存修改';
    cancelBtn.style.display = 'inline-block';
    formTitle.textContent = '修改人员信息';

    document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
}

/**
 * 重置表单状态为新增
 */
function resetFormState() {
    form.reset();
    isEditingInput.value = 'false';
    originalStudentIdInput.value = '';
    document.getElementById('id').disabled = false; 
    
    submitBtn.textContent = '新增';
    submitBtn.className = 'btn btn-primary';
    cancelBtn.style.display = 'none';
    formTitle.textContent = '人员信息表单';
}


form.addEventListener('submit', submitPersonnel);
cancelBtn.addEventListener('click', resetFormState);

// 初始加载数据
window.onload = fetchPersonnelData;