<?php
$servername = "localhost";
$username = "tcc_user"; // colocar o username do seu DB
$password = "**********"; // colocar a senha do seu DB
$dbname = "site";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT id, nome, descricao, preco, quantidade FROM produtos";
$result = $conn->query($sql);
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechFin - Dashboard Corporativo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 40px 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            border-top: 4px solid #00ff88;
        }
        h1 {
            text-align: center;
            font-weight: 300;
            margin-bottom: 30px;
            color: #ffffff;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 16px;
            background-color: #2a2a2a;
            border-radius: 4px;
            overflow: hidden;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        th {
            background-color: #121212;
            color: #00ff88;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 14px;
            letter-spacing: 1px;
        }
        tr:hover {
            background-color: #333333;
        }
        tr:last-child td {
            border-bottom: none;
        }
        .vazio {
            text-align: center;
            color: #aaaaaa;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Painel de Controle de Ativos</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Ativo</th>
                <th>Descrição do Portfólio</th>
                <th>Valor (R$)</th>
                <th>Volume</th>
            </tr>
            <?php
            if ($result->num_rows > 0) {
                while($row = $result->fetch_assoc()) {
                    echo "<tr>
                            <td>" . $row["id"]. "</td>
                            <td>" . $row["nome"]. "</td>
                            <td>" . $row["descricao"]. "</td>
                            <td>" . number_format($row["preco"], 2, ',', '.'). "</td>
                            <td>" . $row["quantidade"]. "</td>
                          </tr>";
                }
            } else {
                echo "<tr><td colspan='5' class='vazio'>Nenhum ativo registrado no sistema.</td></tr>";
            }
            ?>
        </table>
    </div>
</body>
</html>

<?php
$conn->close();
?>
