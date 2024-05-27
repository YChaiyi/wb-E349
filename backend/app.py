from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import uuid
import jwt
import time
import os
import base64

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域资源共享

# MySQL 数据库连接配置
db_config = {
    'host': 'localhost',  # 数据库主机地址
    'user': 'wb_E340',       # 数据库用户名
    'password': '*****',  # 数据库密码
    'database': 'wb_E340'  # 数据库名称
}

# JWT 加密密钥
JWT_SECRET_KEY = 'dsuayioho'

# 定义保存图片的目录
UPLOAD_FOLDER = './uploads'

def validate_token(token, user_type, return_uuid=False):
    try:
        # 解密JWT令牌
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        if user_type == 'user':
            uuid = payload['uuid']
        elif user_type == 'admin':
            uuid = payload['id']
        timestamp = payload['timestamp']

        # 检查时间戳是否超过30天
        current_timestamp = int(time.time())
        if current_timestamp - timestamp > 30 * 24 * 60 * 60:
            return False, '令牌已过期', None

        # 连接 MySQL 数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if user_type == 'user':
            # 查询 user_info 表中是否存在匹配的UUID和token
            query = "SELECT * FROM user_info WHERE uuid = %s AND jwt_token = %s"
        elif user_type == 'admin':
            # 查询 admin_user 表中是否存在匹配的ID和token
            query = "SELECT * FROM admin_user WHERE id = %s AND jwt_token = %s"
        else:
            return False, '无效的用户类型', None

        cursor.execute(query, (uuid, token))
        result = cursor.fetchone()  # 获取查询结果的第一行

        if result:
            if return_uuid and user_type == 'user':
                return True, None, uuid  # 令牌有效,返回UUID
            elif return_uuid and user_type == 'admin':
                return True, None, uuid  # 令牌有效,返回UUID
            else:
                return True, None, None  # 令牌有效,不返回UUID
        else:
            return False, '令牌无效', None

    except jwt.DecodeError:
        return False, '令牌无效', None

    except mysql.connector.Error as error:
        # 捕获 MySQL 错误并返回错误信息
        return False, str(error), None

    finally:
        # 关闭数据库连接
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            educationid:
              type: string
              description: 用户的教育ID
            name:
              type: string
              description: 用户姓名
            password:
              type: string
              description: 用户密码明文
    responses:
      200:
        description: 注册成功
        schema:
          properties:
            message:
              type: string
              description: 注册成功提示信息
      400:
        description: 注册失败,姓名不匹配或未知用户
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 获取请求体中的 JSON 数据
    educationid = data.get('educationid')  # 获取请求数据中的 educationid
    name = data.get('name')  # 获取请求数据中的 name
    password = data.get('password')  # 获取请求数据中的 password

    try:
        # 连接 MySQL 数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 查询 education_info 表中是否存在该 educationid
        query = "SELECT * FROM education_info WHERE educationid = %s"
        cursor.execute(query, (educationid,))
        result = cursor.fetchone()  # 获取查询结果的第一行

        if result:
            # 检查姓名是否匹配
            if result[1] == name:
                # 生成唯一的 UUID
                user_uuid = str(uuid.uuid4())

                # 将用户信息插入到新的用户信息表中
                insert_query = "INSERT INTO user_info (uuid, educationid, name, password, jwt_token, points) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (user_uuid, educationid, name, password, 'unknown', 0))
                conn.commit()  # 提交事务

                return jsonify({'message': '注册成功'})
            else:
                return jsonify({'error': '姓名不匹配'}), 400
        else:
            return jsonify({'error': '未知用户'}), 400

    except mysql.connector.Error as error:
        # 捕获 MySQL 错误并返回错误信息
        return jsonify({'error': str(error)}), 500

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            educationid:
              type: string
              description: 用户的教育ID
            password:
              type: string
              description: 用户密码
    responses:
      200:
        description: 登录成功
        schema:
          properties:
            token:
              type: string
              description: JWT令牌
      400:
        description: 登录失败,教育ID或密码错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 获取请求体中的 JSON 数据
    educationid = data.get('educationid')  # 获取请求数据中的 educationid
    password = data.get('password')  # 获取请求数据中的 password

    try:
        # 连接 MySQL 数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 查询 user_info 表中是否存在该用户
        query = "SELECT * FROM user_info WHERE educationid = %s AND password = %s"
        cursor.execute(query, (educationid, password))
        result = cursor.fetchone()  # 获取查询结果的第一行

        if result:
            # 生成包含时间戳和UUID的JWT令牌
            timestamp = int(time.time())
            payload = {
                'timestamp': timestamp,
                'uuid': result[1]
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

            # 更新数据库中的JWT令牌
            update_query = "UPDATE user_info SET jwt_token = %s WHERE educationid = %s"
            cursor.execute(update_query, (token, educationid))
            conn.commit()  # 提交事务

            return jsonify({'token': token})
        else:
            return jsonify({'error': '教育ID或密码错误'}), 400

    except mysql.connector.Error as error:
        # 捕获 MySQL 错误并返回错误信息
        return jsonify({'error': str(error)}), 500

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()

@app.route('/admin_register', methods=['POST'])
def admin_register():
    """
    管理员注册接口
    ---
    tags:
      - 管理员管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            facultyid:
              type: string
              description: 管理员的教职工ID
            name:
              type: string
              description: 管理员姓名
            password:
              type: string
              description: 管理员密码明文
    responses:
      200:
        description: 注册成功
        schema:
          properties:
            message:
              type: string
              description: 注册成功提示信息
      400:
        description: 注册失败,姓名不匹配或未知管理员
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 获取请求体中的 JSON 数据
    facultyid = data.get('facultyid')  # 获取请求数据中的 facultyid
    name = data.get('name')  # 获取请求数据中的 name
    password = data.get('password')  # 获取请求数据中的 password

    try:
        # 连接 MySQL 数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 查询 faculty_info 表中是否存在该 facultyid
        query = "SELECT facultyid, name FROM faculty_info WHERE facultyid = %s"
        cursor.execute(query, (facultyid,))
        result = cursor.fetchone()  # 获取查询结果的第一行

        if result:
            # 检查姓名是否匹配
            if result[1] == name:
                # 将管理员信息插入到 admin_user 表中
                insert_query = "INSERT INTO admin_user (facultyid, name, password, jwt_token) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (facultyid, result[1], password, 'unknown'))
                conn.commit()  # 提交事务

                return jsonify({'message': '注册成功'})
            else:
                return jsonify({'error': '姓名不匹配'}), 400
        else:
            return jsonify({'error': '未知管理员'}), 400

    except mysql.connector.Error as error:
        # 捕获 MySQL 错误并返回错误信息
        return jsonify({'error': str(error)}), 500

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()

@app.route('/admin_login', methods=['POST'])
def admin_login():
    """
    管理员登录接口
    ---
    tags:
      - 管理员管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            facultyid:
              type: string
              description: 管理员的教职工ID
            password:
              type: string
              description: 管理员密码
    responses:
      200:
        description: 登录成功
        schema:
          properties:
            token:
              type: string
              description: JWT令牌
      400:
        description: 登录失败,教职工ID或密码错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()
    facultyid = data.get('facultyid')
    password = data.get('password')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 查询管理员用户信息表中是否存在该管理员
        query = "SELECT * FROM admin_user WHERE facultyid = %s AND password = %s"
        cursor.execute(query, (facultyid, password))
        result = cursor.fetchone()

        if result:
            # 生成包含时间戳和管理员ID的JWT令牌
            timestamp = int(time.time())
            payload = {
                'timestamp': timestamp,
                'id': result[0]
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

            # 更新数据库中的JWT令牌
            update_query = "UPDATE admin_user SET jwt_token = %s WHERE id = %s"
            cursor.execute(update_query, (token, result[0]))
            conn.commit()

            return jsonify({'token': token})
        else:
            return jsonify({'error': '教职工ID或密码错误'}), 400

    except mysql.connector.Error as error:
        return jsonify({'error': str(error)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/validate_token', methods=['POST'])
def validate_token_route():
    """
    验证token有效性接口
    ---
    tags:
      - 验证
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            user_type:
              type: string
              description: 用户类型,可选值为 "user" 或 "admin"
            token:
              type: string
              description: JWT令牌
    responses:
      200:
        description: 令牌有效
        schema:
          properties:
            message:
              type: string
              description: 令牌有效提示信息
      400:
        description: 令牌无效或过期
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 获取请求体中的 JSON 数据
    user_type = data.get('user_type')  # 获取请求数据中的 user_type
    token = data.get('token')  # 获取请求数据中的 token

    is_valid, error_message, _ = validate_token(token, user_type)

    if is_valid:
        return jsonify({'message': '令牌有效'})
    else:
        if error_message == '令牌已过期':
            return jsonify({'error': error_message}), 400
        elif error_message == '令牌无效':
            return jsonify({'error': error_message}), 400
        elif error_message == '无效的用户类型':
            return jsonify({'error': error_message}), 400
        else:
            return jsonify({'error': error_message}), 500

@app.route('/change_password', methods=['POST'])
def change_password():
    """
    修改用户密码接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
            current_password:
              type: string
              description: 当前密码明文
            new_password:
              type: string
              description: 新密码明文
    responses:
      200:
        description: 密码修改成功
        schema:
          properties:
            message:
              type: string
              description: 密码修改成功提示信息
      400:
        description: 请求参数不完整或密码错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()
    token = data.get('token')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not all([token, current_password, new_password]):
        return jsonify({'error': '请求参数不完整'}), 400

    is_valid, error_message, uuid = validate_token(token, 'user', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM user_info WHERE uuid = %s", (uuid,))
        result = cursor.fetchone()
        if result and result[0] == current_password:
            cursor.execute("UPDATE user_info SET password = %s WHERE uuid = %s", (new_password, uuid))
            conn.commit()
        else:
            return jsonify({'error': '当前密码错误'}), 400
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return jsonify({'message': '密码修改成功'}), 200
  
@app.route('/change_admin_password', methods=['POST'])
def change_admin_password():
    """
    修改管理员密码接口
    ---
    tags:
      - 管理员管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 管理员令牌
            current_password:
              type: string
              description: 当前密码明文
            new_password:
              type: string
              description: 新密码明文
    responses:
      200:
        description: 密码修改成功
        schema:
          properties:
            message:
              type: string
              description: 密码修改成功提示信息
      400:
        description: 请求参数不完整或密码错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 管理员令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()
    token = data.get('token')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not all([token, current_password, new_password]):
        return jsonify({'error': '请求参数不完整'}), 400

    is_valid, error_message, admin_id = validate_token(token, 'admin', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM admin_user WHERE id = %s", (admin_id,))
        result = cursor.fetchone()
        if result and result[0] == current_password:
            cursor.execute("UPDATE admin_user SET password = %s WHERE id = %s", (new_password, admin_id))
            conn.commit()
        else:
            return jsonify({'error': '当前密码错误'}), 400
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return jsonify({'message': '密码修改成功'}), 200

@app.route('/update_user_info', methods=['POST'])
def update_user_info():
    """
    更新用户信息接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
            field_name:
              type: string
              description: 要更新的字段名(college或grade或class)
            new_text:
              type: string
              description: 修改后的字段文本
    responses:
      200:
        description: 更新成功
        schema:
          properties:
            message:
              type: string
              description: 更新成功提示信息
      400:
        description: 请求参数不完整或字段名无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()
    token = data.get('token')
    field_name = data.get('field_name')
    new_text = data.get('new_text')

    # 验证 token 并获取 UUID
    is_valid, error_message, uuid = validate_token(token, 'user', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    # 检查请求参数是否完整
    if not all([field_name, new_text]) or field_name not in ['college', 'grade', 'class']:
        return jsonify({'error': '请求参数不完整或字段名无效'}), 400

    # 更新数据库中的用户信息
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        update_query = f"UPDATE user_info SET {field_name} = %s WHERE uuid = %s"
        cursor.execute(update_query, (new_text, uuid))
        conn.commit()
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': '用户信息更新成功'}), 200

#账户控制路由部分结束------------------------------------------------------------------------------------------------------------------------------------账户控制路由部分结束

@app.route('/disposal_record', methods=['POST'])
def create_disposal_record():
    """
    创建投放记录接口
    ---
    tags:
      - 投放记录管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
            image_base64:
              type: string
              description: 投放垃圾图片的 base64 编码
            device_id:
              type: string
              description: 投放设备点位 ID
            waste_type:
              type: string
              description: 投放垃圾类型
    responses:
      20:
        description: 创建成功
        schema:
          properties:
            message:
              type: string
              description: 创建成功提示信息
      400:
        description: 请求参数不完整
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取 JSON 数据
    token = data.get('token')  # 从 JSON 数据中获取令牌

    is_valid, error_message, user_uuid = validate_token(token, 'user', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    # 获取请求参数
    image_base64 = data.get('image_base64')
    device_id = data.get('device_id')
    waste_type = data.get('waste_type')

    # 检查参数是否完整
    if not all([image_base64, device_id, waste_type]):
        return jsonify({'error': '请求参数不完整'}), 400

    # 将图片保存到服务器
    try:
        # 检查 image_base64 是否以 "data:image" 开头
        if image_base64.startswith("data:image"):
            # 移除 "data:image" 前缀
            image_data = base64.b64decode(image_base64.split(',')[1])
        else:
            image_data = base64.b64decode(image_base64)
            
        image_uuid = str(uuid.uuid4())
        image_path = os.path.join(UPLOAD_FOLDER, f"{image_uuid}.jpg")
        with open(image_path, 'wb') as f:
            f.write(image_data)
    except Exception as e:
        print(e)
        return jsonify({'error': '图片保存失败'}), 500

    # 将数据插入数据库
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_disposal_records (user_uuid, image_path, device_id, waste_type)
            VALUES (%s, %s, %s, %s)
        ''', (user_uuid, image_path, device_id, waste_type))
        conn.commit()
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': '投放记录创建成功'}), 200

@app.route('/user_info', methods=['POST'])
def user_info():
    """
    获取用户信息接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌  
    responses:
      200:
        description: 获取成功
        schema:
          properties:
            educationid:
              type: string
              description: 用户教育ID
            name:
              type: string
              description: 用户名
            points:
              type: integer
              description: 用户积分
            college:
              type: string
              description: 用户学院，可能为NULL
            class:
              type: string
              description: 用户班级，可能为NULL
            grade:
              type: string
              description: 用户年级，可能为NULL
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string  
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取JSON数据
    token = data.get('token')  # 从JSON数据中获取令牌

    is_valid, error_message, uuid = validate_token(token, 'user', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT educationid, name, points, college, class, grade
            FROM user_info
            WHERE uuid = %s
        ''', (uuid,))
        result = cursor.fetchone()
        if result:
            educationid, name, points, college, class_, grade = result
            return jsonify({
                'educationid': educationid,
                'name': name,
                'points': points,
                'college': college,
                'class': class_,
                'grade': grade
            }), 200
        else:
            return jsonify({'error': '未找到用户信息'}), 404
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/user_disposal_records', methods=['POST'])
def get_user_disposal_records():
    """
    获取用户垃圾投放记录接口
    ---
    tags:
      - 用户垃圾投放记录管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
    responses:
      200:
        description: 获取成功
        schema:
          properties:
            records:
              type: object
              description: 用户的垃圾投放记录，以记录ID为键
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      404:
        description: 未找到记录
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取 JSON 数据
    token = data.get('token')  # 从 JSON 数据中获取令牌

    is_valid, error_message, user_uuid = validate_token(token, 'user', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, image_path, device_id, waste_type, created_at
            FROM user_disposal_records
            WHERE user_uuid = %s
            ORDER BY created_at DESC
        ''', (user_uuid,))
        results = cursor.fetchall()
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

    if not results:
        return jsonify({'error': '未找到记录'}), 404

    records = {}
    for record in results:
        record_id, image_path, device_id, waste_type, created_at = record
        image_filename = os.path.basename(image_path)  # 获取文件名部分
        records[str(record_id)] = {
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'device_id': device_id,
            'image_filename': image_filename,  # 返回文件名而不是完整路径
            'waste_type': waste_type
        }

    return jsonify(records), 200

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def download_file(filename):
    # 使用send_from_directory安全地发送文件
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_devices', methods=['POST'])
def get_devices():
    """
    获取设备列表接口
    ---
    tags:
      - 设备管理
    responses:
      200:
        description: 请求成功
        schema:
          properties:
            devices:
              type: object
              description: 设备列表，每个设备包含id和描述
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT device_id, description FROM devices")
        rows = cursor.fetchall()
        
        devices = {}
        for index, (device_id, description) in enumerate(rows, start=1):
            devices[str(index)] = {"device_id": str(device_id), "describe": description}
        
        return jsonify(devices), 200
    except mysql.connector.Error as e:
        print(e)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/get_disposal_types', methods=['POST'])
def get_disposal_types():
    """
    获取垃圾类型列表接口
    ---
    tags:
      - 垃圾管理
    responses:
      200:
        description: 请求成功
        schema:
          properties:
            disposal_types:
              type: object
              description: 垃圾类型列表，每个类型包含id和描述
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT device_id, description FROM disposal_type")
        rows = cursor.fetchall()
        
        disposal_types = {}
        for index, (device_id, description) in enumerate(rows, start=1):
            disposal_types[str(index)] = {"device_id": str(device_id), "description": description}
        
        return jsonify(disposal_types), 200
    except mysql.connector.Error as e:
        print(e)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

#客户端功能路由部分结束------------------------------------------------------------------------------------------------------------------------------------客户端功能路由部分结束

@app.route('/admin_info', methods=['POST'])
def admin_info():
    """
    获取管理员信息接口
    ---
    tags:
      - 管理员管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 管理员令牌  
    responses:
      200:
        description: 获取成功
        schema:
          properties:
            facultyid:
              type: string
              description: 教职工ID
            name:
              type: string
              description: 管理员姓名
      401:
        description: 管理员令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string  
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取JSON数据
    token = data.get('token')  # 从JSON数据中获取令牌

    is_valid, error_message, uuid = validate_token(token, 'admin', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT facultyid, name
            FROM admin_user
            WHERE id = %s
        ''', (uuid,))
        result = cursor.fetchone()
        if result:
            facultyid, name = result
            return jsonify({
                'facultyid': facultyid,
                'name': name
            }), 200
        else:
            return jsonify({'error': '未找到管理员信息'}), 404
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/admin_disposal_records', methods=['POST'])
def get_admin_disposal_records():
    """
    获取所有用户垃圾投放记录接口（管理员使用）
    ---
    tags:
      - 管理员垃圾投放记录管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 管理员令牌
    responses:
      200:
        description: 获取成功
        schema:
          properties:
            records:
              type: object
              description: 所有用户的垃圾投放记录，以记录ID为键
      401:
        description: 管理员令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取 JSON 数据
    token = data.get('token')  # 从 JSON 数据中获取令牌

    is_valid, error_message, _ = validate_token(token, 'admin')  # 接收三个返回值，忽略第三个
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT udr.id, udr.image_path, udr.device_id, udr.waste_type, udr.created_at, udr.point_status, udr.user_uuid, ui.educationid, ui.name
            FROM user_disposal_records udr
            LEFT JOIN user_info ui ON udr.user_uuid = ui.uuid
            ORDER BY udr.created_at DESC
        ''')
        results = cursor.fetchall()
    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

    records = {}
    for record in results:
        record_id, image_path, device_id, waste_type, created_at, point_status, user_uuid, educationid, name = record
        image_filename = os.path.basename(image_path)  # 获取文件名部分
        # 处理 point_status 字段
        if point_status is None:
            point_status_value = "false"
        elif point_status == True:
            point_status_value = "true"
        else:
            point_status_value = point_status  # 直接返回文本

        records[str(record_id)] = {
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'device_id': device_id,
            'image_filename': image_filename,  # 返回文件名而不是完整路径
            'waste_type': waste_type,
            'point_status': point_status_value,  # 添加 point_status 到返回的记录中
            'user_uuid': user_uuid,
            'educationid': educationid,
            'name': name
        }

    return jsonify(records), 200

@app.route('/update_points', methods=['POST'])
def update_points():
    """
    更新用户积分接口
    ---
    tags:
      - 积分管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
            disposal_record_id:
              type: integer
              description: 投放记录ID
    responses:
      200:
        description: 积分更新成功
        schema:
          properties:
            message:
              type: string
              description: 积分更新成功提示信息
      400:
        description: 请求参数不完整
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取 JSON 数据
    token = data.get('token')  # 从 JSON 数据中获取令牌
    disposal_record_id = data.get('disposal_record_id')  # 从 JSON 数据中获取投放记录ID

    if not token or disposal_record_id is None:
        return jsonify({'error': '请求参数不完整'}), 400

    is_valid, error_message, _ = validate_token(token, 'admin')
    if not is_valid:
        return jsonify({'error': error_message}), 401

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 查询投放记录中的用户UUID
        cursor.execute("SELECT user_uuid FROM user_disposal_records WHERE id = %s", (disposal_record_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': '未找到对应的投放记录'}), 400
        user_uuid = result[0]

        # 更新用户信息表中的积分
        cursor.execute("UPDATE user_info SET points = points + 1 WHERE uuid = %s", (user_uuid,))
        conn.commit()

        # 更新投放记录的point_status字段
        cursor.execute("UPDATE user_disposal_records SET point_status = 'true' WHERE id = %s", (disposal_record_id,))
        conn.commit()

    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': '积分更新成功'}), 200
  
@app.route('/manage_device', methods=['POST'])
def manage_device():
    """
    设备管理接口
    ---
    tags:
      - 设备管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
            action:
              type: string
              description: 操作类型 (add, delete, update)
            device_id:
              type: integer
              description: 设备ID (用于删除和更新)
            description:
              type: string
              description: 设备描述 (用于添加和更新)
    responses:
      200:
        description: 操作成功
        schema:
          properties:
            message:
              type: string
              description: 成功提示信息
      400:
        description: 请求参数不完整
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取 JSON 数据
    token = data.get('token')  # 从 JSON 数据中获取令牌

    is_valid, error_message, user_uuid = validate_token(token, 'admin', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    # 获取请求参数
    action = data.get('action')
    device_id = data.get('device_id')
    description = data.get('description')

    # 检查参数是否完整
    if not action:
        return jsonify({'error': '请求参数不完整'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if action == 'add':
            if not description:
                return jsonify({'error': '请求参数不完整'}), 400
            cursor.execute('INSERT INTO devices (description) VALUES (%s)', (description,))
            conn.commit()
            return jsonify({'message': '设备添加成功'}), 200

        elif action == 'delete':
            if not device_id:
                return jsonify({'error': '请求参数不完整'}), 400
            cursor.execute('DELETE FROM devices WHERE device_id = %s', (device_id,))
            conn.commit()
            return jsonify({'message': '设备删除成功'}), 200

        elif action == 'update':
            if not device_id or not description:
                return jsonify({'error': '请求参数不完整'}), 400
            cursor.execute('UPDATE devices SET description = %s WHERE device_id = %s', (description, device_id))
            conn.commit()
            return jsonify({'message': '设备更新成功'}), 200

        else:
            return jsonify({'error': '无效的操作类型'}), 400

    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/manage_disposal_type', methods=['POST'])
def manage_disposal_type():
    """
    垃圾类型管理接口
    ---
    tags:
      - 垃圾类型管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 用户令牌
            action:
              type: string
              description: 操作类型 (add, delete, update)
            device_id:
              type: integer
              description: 类型ID (用于删除和更新)
            description:
              type: string
              description: 类型描述 (用于添加和更新)
    responses:
      200:
        description: 操作成功
        schema:
          properties:
            message:
              type: string
              description: 成功提示信息
      400:
        description: 请求参数不完整
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 用户令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()  # 从请求体中获取 JSON 数据
    token = data.get('token')  # 从 JSON 数据中获取令牌

    is_valid, error_message, user_uuid = validate_token(token, 'admin', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    # 获取请求参数
    action = data.get('action')
    device_id = data.get('device_id')
    description = data.get('description')

    # 检查参数是否完整
    if not action:
        return jsonify({'error': '请求参数不完整'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if action == 'add':
            if not description:
                return jsonify({'error': '请求参数不完整'}), 400
            cursor.execute('INSERT INTO disposal_type (description) VALUES (%s)', (description,))
            conn.commit()
            return jsonify({'message': '垃圾类型添加成功'}), 200

        elif action == 'delete':
            if not device_id:
                return jsonify({'error': '请求参数不完整'}), 400
            cursor.execute('DELETE FROM disposal_type WHERE device_id = %s', (device_id,))
            conn.commit()
            return jsonify({'message': '垃圾类型删除成功'}), 200

        elif action == 'update':
            if not device_id or not description:
                return jsonify({'error': '请求参数不完整'}), 400
            cursor.execute('UPDATE disposal_type SET description = %s WHERE device_id = %s', (description, device_id))
            conn.commit()
            return jsonify({'message': '垃圾类型更新成功'}), 200

        else:
            return jsonify({'error': '无效的操作类型'}), 400

    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_users', methods=['POST'])
def get_users():
    """
    获取所有用户信息的接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: 管理员token
    responses:
      200:
        description: 请求成功
        schema:
          type: object
          properties:
            users:
              type: object
              description: 用户信息列表，每个用户包含uuid、educationid、name、password、points、college、grade、class字段
      401:
        description: 鉴权失败
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()
    token = data.get('token')
    is_valid, error_message, uuid = validate_token(token, 'admin', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401  # 返回错误响应,状态码为401 Unauthorized

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT uuid, educationid, name, password, points, college, grade, class FROM user_info")
        rows = cursor.fetchall()

        users = {str(index): row for index, row in enumerate(rows, start=1)}

        return jsonify(users), 200
    except mysql.connector.Error as e:
        print(e)
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/manage_user', methods=['POST'])
def manage_user():
    """
    管理用户接口
    ---
    tags:
      - 用户管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            token:
              type: string
              description: 管理员令牌
            action:
              type: string
              description: 操作类型 ('delete', 'update_name', 'update_educationid', 'update_points', 'update_college', 'update_grade', 'update_class', 'change_password')
            uuid:
              type: string
              description: 要操作用户对象的UUID
            new_value:
              type: string
              description: 新值 (仅当 action 为 'update_name', 'update_educationid', 'update_points', 'update_college', 'update_grade', 'update_class' 类型时需要)
            new_password:
              type: string
              description: 新密码 (仅当 action 为 'change_password' 类型时需要)
    responses:
      200:
        description: 操作成功
        schema:
          properties:
            message:
              type: string
              description: 操作成功提示信息
      400:
        description: 请求参数不完整或无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      401:
        description: 管理员令牌无效
        schema:
          properties:
            error:
              type: string
              description: 错误信息
      500:
        description: 服务器内部错误
        schema:
          properties:
            error:
              type: string
              description: 错误信息
    """
    data = request.get_json()
    token = data.get('token')
    action = data.get('action')
    user_uuid = data.get('uuid')

    # 验证管理员令牌
    is_valid, error_message, admin_uuid = validate_token(token, 'admin', return_uuid=True)
    if not is_valid:
        return jsonify({'error': error_message}), 401

    # 检查必要的参数
    if not all([action, user_uuid]):
        return jsonify({'error': '请求参数不完整'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if action == 'delete':
            # 删除用户操作
            cursor.execute('DELETE FROM user_info WHERE id = %s', (user_uuid,))
        
        elif action.startswith('update_'):
            # 更新用户信息操作
            field_name = action.replace('update_', '')
            new_value = data.get('new_value')
            if not new_value:
                return jsonify({'error': '缺少新值'}), 400
            
            cursor.execute(f'UPDATE user_info SET {field_name} = %s WHERE id = %s', (new_value, user_uuid))
        
        elif action == 'change_password':
            # 更改用户密码操作
            new_password = data.get('new_password')
            if not new_password:
                return jsonify({'error': '缺少新密码'}), 400
            
            # 在这里直接使用明文密码进行更新
            cursor.execute('UPDATE user_info SET password = %s WHERE id = %s', (new_password, user_uuid))
        
        else:
            return jsonify({'error': '无效的操作类型'}), 400

        conn.commit()
        return jsonify({'message': '操作成功'}), 200

    except mysql.connector.Error as error:
        print(error)
        return jsonify({'error': '服务器内部错误'}), 500
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="38920")  # 运行 Flask 应用
