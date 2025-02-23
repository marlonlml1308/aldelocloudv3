<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Modules extends Model
{
    public static function getModuleName($moduleId)
    {
        return self::where('id', $moduleId)->value('name') ?? 'Desconocido';
    }
}
