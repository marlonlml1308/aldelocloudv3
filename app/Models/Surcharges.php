<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Surcharges extends Model
{
    public static function getSName($sId)
    {
        return self::where('id', $sId)->value('surchargetext') ?? 'Desconocido';
    }
}
