<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Paymenttypes extends Model
{
    protected $table = 'payment_types';
    public static function getPTName($ptId)
    {
        return self::where('id', $ptId)->value('name') ?? 'Desconocido';
    }
}
