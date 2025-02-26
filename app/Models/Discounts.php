<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Discounts extends Model
{
    public static function getDName($dId)
    {
        return self::where('id', $dId)->value('discounttext') ?? 'Desconocido';
    }
}
