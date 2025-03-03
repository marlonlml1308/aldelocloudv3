<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Taxes extends Model
{
    public static function getTaxName($taxId)
    {
        return self::where('id', $taxId)->value('taxname') ?? 'Desconocido';
    }
    // En App\Models\Taxes.php
    public static function getTaxPercent(int $taxId): float
    {
        return (float) self::where('id', $taxId)->value('taxpercent');
    }

}
