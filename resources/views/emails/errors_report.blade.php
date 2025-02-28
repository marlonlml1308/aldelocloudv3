<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte Diario de Errores</title>
</head>
<body class="font-sans antialiased dark:bg-black dark:text-white/50">
    <h1>Reporte Diario de Errores (errorsmdb)</h1>
    <ul>
        @foreach($errors as $error)
            <li>
                ID: {{ $error->idtable }} - Nombre: {{ $error->name }} - Tabla: {{ $error->table }} - Fecha: {{ $error->created_at }}
            </li>
        @endforeach
    </ul>
</body>
</html>
