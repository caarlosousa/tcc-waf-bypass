<?php
session_start();
$mensagem = "";

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $servername = "localhost";
    $username = "tcc_user"; // colocar o username do seu DB
    $password = "**********"; // colocar a senha do seu DB
    $dbname = "site";

    // Oculta erros na tela para forçar o cenário Blind SQLi
    error_reporting(0);
    mysqli_report(MYSQLI_REPORT_STRICT);

    try {
        $conn = new mysqli($servername, $username, $password, $dbname);

        $usuario = $_POST['usuario'];
        $senha = $_POST['senha'];

        // Consulta vulnerável
        $sql = "SELECT * FROM usuarios WHERE usuario='$usuario' AND senha='$senha'";
        $result = $conn->query($sql);

        if ($result && $result->num_rows > 0) {
            $_SESSION['logado'] = true;
            // Guarda o texto na variável ao invés de usar echo
            $mensagem = "<span class='sucesso'>Login realizado com sucesso! Redirecionando...</span>";
            // Redireciona automaticamente para a página de produtos após 2 segundos
            $mensagem .= "<script>setTimeout(function(){ window.location.href = 'index.php'; }, 2000);</script>";
        } else {
            // Guarda o erro na variável ao invés de usar echo
            $mensagem = "<span class='erro'>Usuário ou senha incorretos.</span>";
        }

        $conn->close();

    } catch (Exception $e) {
        // Retorna erro 500 silencioso em caso de payload SQL inválido (ex: ExtractValue)
        http_response_code(500);
        $mensagem = "<span class='erro'>Erro interno do servidor.</span>";
        error_log("Erro de DB capturado: " . $e->getMessage());
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechFin - Portal Administrativo Seguro</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: #1e1e1e;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            width: 100%;
            max-width: 400px;
            border-top: 4px solid #00ff88;
        }
        .login-container h2 {
            text-align: center;
            margin-bottom: 30px;
            font-weight: 300;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #aaaaaa;
            font-size: 14px;
        }
        .input-group input {
            width: 100%;
            padding: 12px;
            background-color: #2a2a2a;
            border: 1px solid #333;
            border-radius: 4px;
            color: #fff;
            box-sizing: border-box;
        }
        .input-group input:focus {
            outline: none;
            border-color: #00ff88;
        }
        .btn-submit {
            width: 100%;
            padding: 12px;
            background-color: #00ff88;
            color: #121212;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn-submit:hover {
            background-color: #00cc6a;
        }
        .mensagem {
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
        .sucesso { color: #00ff88; }
        .erro { color: #ff4444; }
    </style>
</head>
<body>

<div class="login-container">
    <h2>TechFin Admin</h2>

    <form method="POST" action="">
        <div class="input-group">
            <label for="usuario">Credencial de Acesso</label>
            <input type="text" id="usuario" name="usuario" autocomplete="off">
        </div>
        <div class="input-group">
            <label for="senha">Código de Autenticação</label>
            <input type="password" id="senha" name="senha">
        </div>
        <button type="submit" class="btn-submit">Autenticar</button>
    </form>

    <div class="mensagem">
        <?php echo $mensagem; ?>
    </div>
</div>

</body>
</html>
