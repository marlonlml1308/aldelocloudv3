<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
class Products extends Model
{
    Use HasFactory;
    public function categories(): BelongsTo
    {
        return  $this->belongsTo(Categories::class, 'menucategoryid');
    }
    public function groups(): BelongsTo
    {
        return  $this->belongsTo(Groups::class, 'menugroupid');
    }
    public static function getTaxNames()
    {
        return \App\Models\Taxes::pluck('taxname', 'id')->toArray();
    }
    public static function getTaxOptions()
    {
        return Taxes::pluck('taxname', 'id')->toArray();
    }
        public static function getModuleName($moduleId)
    {
        return self::where('id', $moduleId)->value('taxname') ?? 'Desconocido';
    }
    public function getPriceWithTaxAttribute()
    {
        // Aseguramos que defaultunitprice tenga un valor numérico
        $basePrice = $this->defaultunitprice ?? 0;
        $taxTotal = 0;

        // Sumamos los porcentajes si los impuestos están activos
        if ($this->menuitemtaxable) {
            $taxTotal += \App\Models\Taxes::getTaxPercent(1) ?? 0;
        }
        if ($this->gstapplied) {
            $taxTotal += \App\Models\Taxes::getTaxPercent(2) ?? 0;
        }
        if ($this->liquortaxapplied) {
            $taxTotal += \App\Models\Taxes::getTaxPercent(3) ?? 0;
        }

        return $basePrice * (1 + ($taxTotal / 100));
    }
    public function children()
    {
        // En esta relación, el campo 'menuitempopupheaderid' en los productos hijos contiene
        // el barcode del producto padre, que es el campo 'barcode' en el modelo padre.
        return $this->hasMany(Products::class, 'menuitempopupheaderid', 'barcode');
    }

    protected static function boot()
    {
        parent::boot();

        static::updated(function ($product) {
            // Verifica que el campo 'menuitemtype' haya cambiado de 2 a 1
            if (
                $product->isDirty('menuitemtype') &&
                $product->menuitemtype == 1 &&
                $product->getOriginal('menuitemtype') == 2
            ) {
                // Actualiza los productos hijos:
                // - menuitempopupheaderid a null,
                // - displayindex a -1,
                // - menuiteminactive a true
                $product->children()->update([
                    'menuitempopupheaderid' => null,
                    'displayindex'           => -1,
                    'menuiteminactive'       => true,
                ]);
            }
        });
    }


}
